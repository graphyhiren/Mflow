import os
import time
import uuid
from unittest import mock

import pytest

from mlflow.entities.model_registry import (
    ModelVersion,
    ModelVersionTag,
    RegisteredModelTag,
)
from mlflow.exceptions import MlflowException
from mlflow.protos.databricks_pb2 import (
    INVALID_PARAMETER_VALUE,
    RESOURCE_DOES_NOT_EXIST,
    ErrorCode,
)
from mlflow.store.model_registry.file_store import FileStore
from mlflow.utils.file_utils import path_to_local_file_uri, write_yaml
from tests.helper_functions import random_int, random_str


def now():
    return int(time.time() * 1000)


@pytest.fixture()
def test_root(tmp_path_factory):
    tmp_path = str(tmp_path_factory.mktemp("test_root") / f"test_file_store_{random_int()}")
    return tmp_path


@pytest.fixture()
def store(test_root):
    return FileStore(test_root)


@pytest.fixture()
def registered_models_names():
    return [random_str() for _ in range(3)]


@pytest.fixture()
def rm_data(registered_models_names, test_root):
    rm_data = {}
    for name in registered_models_names:
        # create registered model
        creation_time = now()
        rm_folder = os.path.join(test_root, FileStore.MODELS_FOLDER_NAME, name)
        os.makedirs(rm_folder)
        d = {
            "name": name,
            "creation_timestamp": creation_time,
            "last_updated_timestamp": creation_time,
            "description": None,
            "latest_versions": [],
            "tags": {},
        }
        rm_data[name] = d
        write_yaml(rm_folder, FileStore.META_DATA_FILE_NAME, d)
        os.makedirs(os.path.join(rm_folder, FileStore.TAGS_FOLDER_NAME))
    return rm_data


def test_create_registered_model(store):

    # Error cases
    with pytest.raises(MlflowException, match="Registered model name cannot be empty."):
        store.create_registered_model(None)
    with pytest.raises(MlflowException, match="Registered model name cannot be empty."):
        store.create_registered_model("")

    name = random_str()
    model = store.create_registered_model(name)
    assert model.name == name
    assert model.latest_versions == []
    assert model.creation_timestamp == model.last_updated_timestamp
    assert model.tags == {}


def _verify_registered_model(fs, name, rm_data):
    rm = fs.get_registered_model(name)
    assert rm.name == name
    assert rm.creation_timestamp == rm_data[name]["creation_timestamp"]
    assert rm.last_updated_timestamp == rm_data[name]["last_updated_timestamp"]
    assert rm.description == rm_data[name]["description"]
    assert rm.latest_versions == rm_data[name]["latest_versions"]
    assert rm.tags == rm_data[name]["tags"]


def test_get_registered_model(store, registered_models_names, rm_data):
    for name in registered_models_names:

        _verify_registered_model(store, name, rm_data)

    # test that fake registered models dont exist.
    for name in {random_str(25) for _ in range(10)}:
        with pytest.raises(
            MlflowException, match=f"Could not find registered model with name {name}"
        ):
            store.get_registered_model(name)


def test_list_registered_model(store, registered_models_names, rm_data):
    for rm in store.list_registered_models(max_results=10, page_token=None):
        name = rm.name
        assert name in registered_models_names, "Not found in registered modules"
        assert name == rm_data[name]["name"]


def test_rename_registered_model(store, registered_models_names, rm_data):
    model_name = registered_models_names[random_int(0, len(registered_models_names) - 1)]
    # Error cases
    with pytest.raises(MlflowException, match=r"Registered model name cannot be empty\."):
        store.rename_registered_model(model_name, None)
    # test that names of existing registered models are checked before renaming

    for name in registered_models_names:
        if name != model_name:
            other_model_name = name
            break
    with pytest.raises(
        MlflowException, match=rf"Registered Model \(name={other_model_name}\) already exists."
    ):
        store.rename_registered_model(model_name, other_model_name)

    new_name = model_name + "!!!"
    assert model_name != new_name
    store.rename_registered_model(model_name, new_name)
    assert store.get_registered_model(new_name).name == new_name


def _extract_names(registered_models):
    return [rm.name for rm in registered_models]


def test_delete_registered_model(store, registered_models_names, rm_data):
    model_name = registered_models_names[random_int(0, len(registered_models_names) - 1)]
    # print(store.list_registered_models(max_results=10, page_token=None))

    # Error cases
    with pytest.raises(
        MlflowException, match=f"Could not find registered model with name {model_name}!!!"
    ):
        store.delete_registered_model(model_name + "!!!")

    store.delete_registered_model(model_name)
    assert model_name not in _extract_names(
        store.list_registered_models(max_results=10, page_token=None)
    )
    # Cannot delete a deleted model
    with pytest.raises(
        MlflowException, match=f"Could not find registered model with name {model_name}"
    ):
        store.delete_registered_model(model_name)


def test_list_registered_model_paginated(store):
    for _ in range(10):
        store.create_registered_model(random_str())
    rms1 = store.list_registered_models(max_results=4, page_token=None)
    assert len(rms1) == 4
    assert rms1.token is not None
    rms2 = store.list_registered_models(max_results=4, page_token=None)
    assert len(rms2) == 4
    assert rms2.token is not None
    assert rms1 == rms2
    rms3 = store.list_registered_models(max_results=500, page_token=rms2.token)
    assert len(rms3) <= 500
    if len(rms3) < 500:
        assert rms3.token is None


def test_list_registered_model_paginated_returns_in_correct_order(store):
    rms = [store.create_registered_model(f"RM{i:03}").name for i in range(50)]

    # test that pagination will return all valid results in sorted order
    # by name ascending
    result = store.list_registered_models(max_results=5, page_token=None)
    assert result.token is not None
    assert _extract_names(result) == rms[0:5]

    result = store.list_registered_models(page_token=result.token, max_results=10)
    assert result.token is not None
    assert _extract_names(result) == rms[5:15]

    result = store.list_registered_models(page_token=result.token, max_results=20)
    assert result.token is not None
    assert _extract_names(result) == rms[15:35]

    result = store.list_registered_models(page_token=result.token, max_results=100)
    assert result.token is None
    assert _extract_names(result) == rms[35:]


def test_list_registered_model_paginated_errors(store):
    rms = [store.create_registered_model(f"RM{i:03}").name for i in range(50)]
    # test that providing a completely invalid page token throws
    with pytest.raises(
        MlflowException, match=r"Invalid page token, could not base64-decode"
    ) as exception_context:
        store.list_registered_models(page_token="evilhax", max_results=20)
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    # test that providing too large of a max_results throws
    with pytest.raises(
        MlflowException, match=r"Invalid value for max_results"
    ) as exception_context:
        store.list_registered_models(page_token="evilhax", max_results=1e15)
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
    # list should not return deleted models
    store.delete_registered_model(name="RM{:03}".format(0))
    assert set(
        _extract_names(store.list_registered_models(max_results=100, page_token=None))
    ) == set(rms[1:])


def _create_model_version(
    fs,
    name,
    source="path/to/source",
    run_id=uuid.uuid4().hex,
    tags=None,
    run_link=None,
    description=None,
):
    return fs.create_model_version(
        name, source, run_id, tags, run_link=run_link, description=description
    )


def _extract_latest_by_stage(latest_versions):
    return {mvd.current_stage: mvd.version for mvd in latest_versions}


def test_get_latest_versions(store):
    name = "test_for_latest_versions"
    rmd1 = store.create_registered_model(name)
    assert rmd1.latest_versions == []

    mv1 = _create_model_version(store, name)
    assert mv1.version == 1
    rmd2 = store.get_registered_model(name)
    assert _extract_latest_by_stage(rmd2.latest_versions) == {"None": 1}

    # add a bunch more
    mv2 = _create_model_version(store, name)
    assert mv2.version == 2
    store.transition_model_version_stage(
        name=mv2.name, version=mv2.version, stage="Production", archive_existing_versions=False
    )

    mv3 = _create_model_version(store, name)
    assert mv3.version == 3
    store.transition_model_version_stage(
        name=mv3.name, version=mv3.version, stage="Production", archive_existing_versions=False
    )
    mv4 = _create_model_version(store, name)
    assert mv4.version == 4
    store.transition_model_version_stage(
        name=mv4.name, version=mv4.version, stage="Staging", archive_existing_versions=False
    )

    # test that correct latest versions are returned for each stage
    rmd4 = store.get_registered_model(name)
    assert _extract_latest_by_stage(rmd4.latest_versions) == {
        "None": 1,
        "Production": 3,
        "Staging": 4,
    }
    assert _extract_latest_by_stage(store.get_latest_versions(name=name, stages=None)) == {
        "None": 1,
        "Production": 3,
        "Staging": 4,
    }
    assert _extract_latest_by_stage(store.get_latest_versions(name=name, stages=[])) == {
        "None": 1,
        "Production": 3,
        "Staging": 4,
    }
    assert _extract_latest_by_stage(
        store.get_latest_versions(name=name, stages=["Production"])
    ) == {"Production": 3}
    assert _extract_latest_by_stage(
        store.get_latest_versions(name=name, stages=["production"])
    ) == {
        "Production": 3
    }  # The stages are case insensitive.
    assert _extract_latest_by_stage(
        store.get_latest_versions(name=name, stages=["pROduction"])
    ) == {
        "Production": 3
    }  # The stages are case insensitive.
    assert _extract_latest_by_stage(
        store.get_latest_versions(name=name, stages=["None", "Production"])
    ) == {"None": 1, "Production": 3}

    # delete latest Production, and should point to previous one
    store.delete_model_version(name=mv3.name, version=mv3.version)
    rmd5 = store.get_registered_model(name=name)
    assert _extract_latest_by_stage(rmd5.latest_versions) == {
        "None": 1,
        "Production": 2,
        "Staging": 4,
    }
    assert _extract_latest_by_stage(store.get_latest_versions(name=name, stages=None)) == {
        "None": 1,
        "Production": 2,
        "Staging": 4,
    }
    assert _extract_latest_by_stage(
        store.get_latest_versions(name=name, stages=["Production"])
    ) == {"Production": 2}


def test_set_registered_model_tag(store):
    name1 = "SetRegisteredModelTag_TestMod"
    name2 = "SetRegisteredModelTag_TestMod 2"
    initial_tags = [
        RegisteredModelTag("key", "value"),
        RegisteredModelTag("anotherKey", "some other value"),
    ]
    store.create_registered_model(name1, initial_tags)
    store.create_registered_model(name2, initial_tags)
    new_tag = RegisteredModelTag("randomTag", "not a random value")
    store.set_registered_model_tag(name1, new_tag)
    rm1 = store.get_registered_model(name=name1)
    all_tags = initial_tags + [new_tag]
    assert rm1.tags == {tag.key: tag.value for tag in all_tags}

    # test overriding a tag with the same key
    overriding_tag = RegisteredModelTag("key", "overriding")
    store.set_registered_model_tag(name1, overriding_tag)
    all_tags = [tag for tag in all_tags if tag.key != "key"] + [overriding_tag]
    rm1 = store.get_registered_model(name=name1)
    assert rm1.tags == {tag.key: tag.value for tag in all_tags}
    # does not affect other models with the same key
    rm2 = store.get_registered_model(name=name2)
    assert rm2.tags == {tag.key: tag.value for tag in initial_tags}

    # can not set tag on deleted (non-existed) registered model
    store.delete_registered_model(name1)
    with pytest.raises(
        MlflowException, match=f"Could not find registered model with name {name1}"
    ) as exception_context:
        store.set_registered_model_tag(name1, overriding_tag)
    assert exception_context.value.error_code == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST)
    # test cannot set tags that are too long
    long_tag = RegisteredModelTag("longTagKey", "a" * 5001)
    with pytest.raises(
        MlflowException,
        match=(r"Registered model value '.+' had length \d+, which exceeded length limit of 5000"),
    ) as exception_context:
        store.set_registered_model_tag(name2, long_tag)
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
    # test can set tags that are somewhat long
    long_tag = RegisteredModelTag("longTagKey", "a" * 4999)
    store.set_registered_model_tag(name2, long_tag)
    # can not set invalid tag
    with pytest.raises(MlflowException, match=r"Tag name cannot be None") as exception_context:
        store.set_registered_model_tag(name2, RegisteredModelTag(key=None, value=""))
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
    # can not use invalid model name
    with pytest.raises(
        MlflowException, match=r"Registered model name cannot be empty"
    ) as exception_context:
        store.set_registered_model_tag(None, RegisteredModelTag(key="key", value="value"))
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)


def test_delete_registered_model_tag(store):
    name1 = "DeleteRegisteredModelTag_TestMod"
    name2 = "DeleteRegisteredModelTag_TestMod 2"
    initial_tags = [
        RegisteredModelTag("key", "value"),
        RegisteredModelTag("anotherKey", "some other value"),
    ]
    store.create_registered_model(name1, initial_tags)
    store.create_registered_model(name2, initial_tags)
    new_tag = RegisteredModelTag("randomTag", "not a random value")
    store.set_registered_model_tag(name1, new_tag)
    store.delete_registered_model_tag(name1, "randomTag")
    rm1 = store.get_registered_model(name=name1)
    assert rm1.tags == {tag.key: tag.value for tag in initial_tags}

    # testing deleting a key does not affect other models with the same key
    store.delete_registered_model_tag(name1, "key")
    rm1 = store.get_registered_model(name=name1)
    rm2 = store.get_registered_model(name=name2)
    assert rm1.tags == {"anotherKey": "some other value"}
    assert rm2.tags == {tag.key: tag.value for tag in initial_tags}

    # delete tag that is already deleted does nothing
    store.delete_registered_model_tag(name1, "key")
    rm1 = store.get_registered_model(name=name1)
    assert rm1.tags == {"anotherKey": "some other value"}

    # can not delete tag on deleted (non-existed) registered model
    store.delete_registered_model(name1)
    with pytest.raises(
        MlflowException, match=f"Could not find registered model with name {name1}"
    ) as exception_context:
        store.delete_registered_model_tag(name1, "anotherKey")
    assert exception_context.value.error_code == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST)
    # can not delete tag with invalid key
    with pytest.raises(MlflowException, match=r"Tag name cannot be None") as exception_context:
        store.delete_registered_model_tag(name2, None)
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
    # can not use invalid model name
    with pytest.raises(
        MlflowException, match=r"Registered model name cannot be empty"
    ) as exception_context:
        store.delete_registered_model_tag(None, "key")
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)


def test_create_model_version(store):
    name = "test_for_create_MV"
    store.create_registered_model(name)
    run_id = uuid.uuid4().hex
    with mock.patch("time.time") as mock_time:
        mock_time.return_value = 456778
        mv1 = store.create_model_version(name, "a/b/CD", run_id)
        assert mv1.name == name
        assert mv1.version == 1

    mvd1 = store.get_model_version(mv1.name, mv1.version)
    assert mvd1.name == name
    assert mvd1.version == 1
    assert mvd1.current_stage == "None"
    assert mvd1.creation_timestamp == 456778000
    assert mvd1.last_updated_timestamp == 456778000
    assert mvd1.description is None
    assert mvd1.source == "a/b/CD"
    assert mvd1.run_id == run_id
    assert mvd1.status == "READY"
    assert mvd1.status_message is None
    assert mvd1.tags == {}

    # new model versions for same name autoincrement versions
    mv2 = _create_model_version(store, name)
    mvd2 = store.get_model_version(name=mv2.name, version=mv2.version)
    assert mv2.version == 2
    assert mvd2.version == 2

    # create model version with tags return model version entity with tags
    tags = [ModelVersionTag("key", "value"), ModelVersionTag("anotherKey", "some other value")]
    mv3 = _create_model_version(store, name, tags=tags)
    mvd3 = store.get_model_version(name=mv3.name, version=mv3.version)
    assert mv3.version == 3
    assert mv3.tags == {tag.key: tag.value for tag in tags}
    assert mvd3.version == 3
    assert mvd3.tags == {tag.key: tag.value for tag in tags}

    # create model versions with runLink
    run_link = "http://localhost:3000/path/to/run/"
    mv4 = _create_model_version(store, name, run_link=run_link)
    mvd4 = store.get_model_version(name, mv4.version)
    assert mv4.version == 4
    assert mv4.run_link == run_link
    assert mvd4.version == 4
    assert mvd4.run_link == run_link

    # create model version with description
    description = "the best model ever"
    mv5 = _create_model_version(store, name, description=description)
    mvd5 = store.get_model_version(name, mv5.version)
    assert mv5.version == 5
    assert mv5.description == description
    assert mvd5.version == 5
    assert mvd5.description == description

    # create model version without runId
    mv6 = _create_model_version(store, name, run_id=None)
    mvd6 = store.get_model_version(name, mv6.version)
    assert mv6.version == 6
    assert mv6.run_id is None
    assert mvd6.version == 6
    assert mvd6.run_id is None


def test_update_model_version(store):
    name = "test_for_update_MV"
    store.create_registered_model(name)
    mv1 = _create_model_version(store, name)
    mvd1 = store.get_model_version(name=mv1.name, version=mv1.version)
    assert mvd1.name == name
    assert mvd1.version == 1
    assert mvd1.current_stage == "None"

    # update stage
    store.transition_model_version_stage(
        name=mv1.name, version=mv1.version, stage="Production", archive_existing_versions=False
    )
    mvd2 = store.get_model_version(name=mv1.name, version=mv1.version)
    assert mvd2.name == name
    assert mvd2.version == 1
    assert mvd2.current_stage == "Production"
    assert mvd2.description is None

    # update description
    store.update_model_version(name=mv1.name, version=mv1.version, description="test model version")
    mvd3 = store.get_model_version(name=mv1.name, version=mv1.version)
    assert mvd3.name == name
    assert mvd3.version == 1
    assert mvd3.current_stage == "Production"
    assert mvd3.description == "test model version"

    # only valid stages can be set
    with pytest.raises(
        MlflowException,
        match=(
            "Invalid Model Version stage: unknown. "
            "Value must be one of None, Staging, Production, Archived."
        ),
    ) as exception_context:
        store.transition_model_version_stage(
            mv1.name, mv1.version, stage="unknown", archive_existing_versions=False
        )
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    # stages are case-insensitive and auto-corrected to system stage names
    for stage_name in ["STAGING", "staging", "StAgInG"]:
        store.transition_model_version_stage(
            name=mv1.name,
            version=mv1.version,
            stage=stage_name,
            archive_existing_versions=False,
        )
        mvd5 = store.get_model_version(name=mv1.name, version=mv1.version)
        assert mvd5.current_stage == "Staging"


def test_transition_model_version_stage_when_archive_existing_versions_is_false(store):
    name = "model"
    store.create_registered_model(name)
    mv1 = _create_model_version(store, name)
    mv2 = _create_model_version(store, name)
    mv3 = _create_model_version(store, name)

    # test that when `archive_existing_versions` is False, transitioning a model version
    # to the inactive stages ("Archived" and "None") does not throw.
    for stage in ["Archived", "None"]:
        store.transition_model_version_stage(name, mv1.version, stage, False)

    store.transition_model_version_stage(name, mv1.version, "Staging", False)
    store.transition_model_version_stage(name, mv2.version, "Production", False)
    store.transition_model_version_stage(name, mv3.version, "Staging", False)

    mvd1 = store.get_model_version(name=name, version=mv1.version)
    mvd2 = store.get_model_version(name=name, version=mv2.version)
    mvd3 = store.get_model_version(name=name, version=mv3.version)

    assert mvd1.current_stage == "Staging"
    assert mvd2.current_stage == "Production"
    assert mvd3.current_stage == "Staging"

    store.transition_model_version_stage(name, mv3.version, "Production", False)

    mvd1 = store.get_model_version(name=name, version=mv1.version)
    mvd2 = store.get_model_version(name=name, version=mv2.version)
    mvd3 = store.get_model_version(name=name, version=mv3.version)

    assert mvd1.current_stage == "Staging"
    assert mvd2.current_stage == "Production"
    assert mvd3.current_stage == "Production"


def test_transition_model_version_stage_when_archive_existing_versions_is_true(store):
    name = "model"
    store.create_registered_model(name)
    mv1 = _create_model_version(store, name)
    mv2 = _create_model_version(store, name)
    mv3 = _create_model_version(store, name)

    msg = (
        r"Model version transition cannot archive existing model versions "
        r"because .+ is not an Active stage"
    )

    # test that when `archive_existing_versions` is True, transitioning a model version
    # to the inactive stages ("Archived" and "None") throws.
    for stage in ["Archived", "None"]:
        with pytest.raises(MlflowException, match=msg):
            store.transition_model_version_stage(name, mv1.version, stage, True)

    store.transition_model_version_stage(name, mv1.version, "Staging", False)
    store.transition_model_version_stage(name, mv2.version, "Production", False)
    store.transition_model_version_stage(name, mv3.version, "Staging", True)

    mvd1 = store.get_model_version(name=name, version=mv1.version)
    mvd2 = store.get_model_version(name=name, version=mv2.version)
    mvd3 = store.get_model_version(name=name, version=mv3.version)

    assert mvd1.current_stage == "Archived"
    assert mvd2.current_stage == "Production"
    assert mvd3.current_stage == "Staging"
    assert mvd1.last_updated_timestamp == mvd3.last_updated_timestamp

    store.transition_model_version_stage(name, mv3.version, "Production", True)

    mvd1 = store.get_model_version(name=name, version=mv1.version)
    mvd2 = store.get_model_version(name=name, version=mv2.version)
    mvd3 = store.get_model_version(name=name, version=mv3.version)

    assert mvd1.current_stage == "Archived"
    assert mvd2.current_stage == "Archived"
    assert mvd3.current_stage == "Production"
    assert mvd2.last_updated_timestamp == mvd3.last_updated_timestamp

    for uncanonical_stage_name in ["STAGING", "staging", "StAgInG"]:
        store.transition_model_version_stage(mv1.name, mv1.version, "Staging", False)
        store.transition_model_version_stage(mv2.name, mv2.version, "None", False)

        # stage names are case-insensitive and auto-corrected to system stage names
        store.transition_model_version_stage(mv2.name, mv2.version, uncanonical_stage_name, True)

        mvd1 = store.get_model_version(name=mv1.name, version=mv1.version)
        mvd2 = store.get_model_version(name=mv2.name, version=mv2.version)
        assert mvd1.current_stage == "Archived"
        assert mvd2.current_stage == "Staging"


def test_delete_model_version(store):
    name = "test_for_delete_MV"
    initial_tags = [
        ModelVersionTag("key", "value"),
        ModelVersionTag("anotherKey", "some other value"),
    ]
    store.create_registered_model(name)
    mv = _create_model_version(store, name, tags=initial_tags)
    mvd = store.get_model_version(name=mv.name, version=mv.version)
    assert mvd.name == name

    store.delete_model_version(name=mv.name, version=mv.version)

    # cannot get a deleted model version
    with pytest.raises(
        MlflowException,
        match=rf"Model Version \(name={mv.name}, version={mv.version}\) not found",
    ) as exception_context:
        store.get_model_version(name=mv.name, version=mv.version)
    assert exception_context.value.error_code == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST)

    # cannot update a delete
    with pytest.raises(
        MlflowException,
        match=rf"Model Version \(name={mv.name}, version={mv.version}\) not found",
    ) as exception_context:
        store.update_model_version(mv.name, mv.version, description="deleted!")
    assert exception_context.value.error_code == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST)

    # cannot delete it again
    with pytest.raises(
        MlflowException,
        match=rf"Model Version \(name={mv.name}, version={mv.version}\) not found",
    ) as exception_context:
        store.delete_model_version(name=mv.name, version=mv.version)
    assert exception_context.value.error_code == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST)


def test_search_model_versions(store):
    # create some model versions
    name = "test_for_search_MV"
    store.create_registered_model(name)
    run_id_1 = uuid.uuid4().hex
    run_id_2 = uuid.uuid4().hex
    run_id_3 = uuid.uuid4().hex
    mv1 = _create_model_version(store, name=name, source="A/B", run_id=run_id_1)
    assert mv1.version == 1
    mv2 = _create_model_version(store, name=name, source="A/C", run_id=run_id_2)
    assert mv2.version == 2
    mv3 = _create_model_version(store, name=name, source="A/D", run_id=run_id_2)
    assert mv3.version == 3
    mv4 = _create_model_version(store, name=name, source="A/D", run_id=run_id_3)
    assert mv4.version == 4

    def search_versions(filter_string):
        return [mvd.version for mvd in store.search_model_versions(filter_string)]

    # search using name should return all 4 versions
    assert set(search_versions("name='%s'" % name)) == {1, 2, 3, 4}

    # search using run_id_1 should return version 1
    assert set(search_versions("run_id='%s'" % run_id_1)) == {1}

    # search using run_id_2 should return versions 2 and 3
    assert set(search_versions("run_id='%s'" % run_id_2)) == {2, 3}

    # search using the IN operator should return all versions
    assert set(search_versions(f"run_id IN ('{run_id_1}','{run_id_2}')")) == {1, 2, 3}

    # search IN operator is case sensitive
    assert set(search_versions(f"run_id IN ('{run_id_1.upper()}','{run_id_2}')")) == {2, 3}

    # search IN operator with right-hand side value containing whitespaces
    assert set(search_versions(f"run_id IN ('{run_id_1}', '{run_id_2}')")) == {1, 2, 3}

    # search using the IN operator with bad lists should return exceptions
    with pytest.raises(
        MlflowException,
        match=(
            r"While parsing a list in the query, "
            r"expected string value, punctuation, or whitespace, "
            r"but got different type in list"
        ),
    ) as exception_context:
        search_versions("run_id IN (1,2,3)")
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    assert set(search_versions(f"run_id LIKE '{run_id_2[:30]}%'")) == {2, 3}

    assert set(search_versions(f"run_id ILIKE '{run_id_2[:30].upper()}%'")) == {2, 3}

    # search using the IN operator with empty lists should return exceptions
    with pytest.raises(
        MlflowException,
        match=(
            r"While parsing a list in the query, "
            r"expected a non-empty list of string values, "
            r"but got empty list"
        ),
    ) as exception_context:
        search_versions("run_id IN ()")
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    # search using an ill-formed IN operator correctly throws exception
    with pytest.raises(
        MlflowException, match=r"Invalid clause\(s\) in filter string"
    ) as exception_context:
        search_versions("run_id IN (")
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    with pytest.raises(
        MlflowException, match=r"Invalid clause\(s\) in filter string"
    ) as exception_context:
        search_versions("run_id IN")
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    with pytest.raises(
        MlflowException, match=r"Invalid clause\(s\) in filter string"
    ) as exception_context:
        search_versions("name LIKE")
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    with pytest.raises(
        MlflowException,
        match=(
            r"While parsing a list in the query, "
            r"expected a non-empty list of string values, "
            r"but got ill-formed list"
        ),
    ) as exception_context:
        search_versions("run_id IN (,)")
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    with pytest.raises(
        MlflowException,
        match=(
            r"While parsing a list in the query, "
            r"expected a non-empty list of string values, "
            r"but got ill-formed list"
        ),
    ) as exception_context:
        search_versions("run_id IN ('runid1',,'runid2')")
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    # delete mv4. search should not return version 4
    store.delete_model_version(name=mv4.name, version=mv4.version)
    assert set(search_versions("")) == {1, 2, 3}

    assert set(search_versions(None)) == {1, 2, 3}

    assert set(search_versions("name='%s'" % name)) == {1, 2, 3}

    store.transition_model_version_stage(
        name=mv1.name, version=mv1.version, stage="production", archive_existing_versions=False
    )

    store.update_model_version(
        name=mv1.name, version=mv1.version, description="Online prediction model!"
    )

    mvds = store.search_model_versions("run_id = '%s'" % run_id_1)
    assert 1 == len(mvds)
    assert isinstance(mvds[0], ModelVersion)
    assert mvds[0].current_stage == "Production"
    assert mvds[0].run_id == run_id_1
    assert mvds[0].source == "A/B"
    assert mvds[0].description == "Online prediction model!"


def test_search_model_versions_by_tag(store):
    # create some model versions
    name = "test_for_search_MV_by_tag"
    store.create_registered_model(name)
    run_id_1 = uuid.uuid4().hex
    run_id_2 = uuid.uuid4().hex

    mv1 = _create_model_version(
        store,
        name=name,
        source="A/B",
        run_id=run_id_1,
        tags=[ModelVersionTag("t1", "abc"), ModelVersionTag("t2", "xyz")],
    )
    assert mv1.version == 1
    mv2 = _create_model_version(
        store,
        name=name,
        source="A/C",
        run_id=run_id_2,
        tags=[ModelVersionTag("t1", "abc"), ModelVersionTag("t2", "x123")],
    )
    assert mv2.version == 2

    def search_versions(filter_string):
        return [mvd.version for mvd in store.search_model_versions(filter_string)]

    assert search_versions(f"name = '{name}' and tag.t2 = 'xyz'") == [1]
    assert search_versions("name = 'wrong_name' and tag.t2 = 'xyz'") == []
    assert search_versions("tag.`t2` = 'xyz'") == [1]
    assert search_versions("tag.t3 = 'xyz'") == []
    assert set(search_versions("tag.t2 != 'xy'")) == {2, 1}
    assert search_versions("tag.t2 LIKE 'xy%'") == [1]
    assert search_versions("tag.t2 LIKE 'xY%'") == []
    assert search_versions("tag.t2 ILIKE 'xY%'") == [1]
    assert set(search_versions("tag.t2 LIKE 'x%'")) == {2, 1}
    assert search_versions("tag.T2 = 'xyz'") == []
    assert search_versions("tag.t1 = 'abc' and tag.t2 = 'xyz'") == [1]
    assert set(search_versions("tag.t1 = 'abc' and tag.t2 LIKE 'x%'")) == {2, 1}
    assert search_versions("tag.t1 = 'abc' and tag.t2 LIKE 'y%'") == []
    # test filter with duplicated keys
    assert search_versions("tag.t2 like 'x%' and tag.t2 != 'xyz'") == [2]


def _search_registered_models(
    fs, filter_string=None, max_results=10, order_by=None, page_token=None
):
    result = fs.search_registered_models(
        filter_string=filter_string,
        max_results=max_results,
        order_by=order_by,
        page_token=page_token,
    )
    return [registered_model.name for registered_model in result], result.token


def test_search_registered_models(store):
    # create some registered models
    prefix = "test_for_search_"
    names = [prefix + name for name in ["RM1", "RM2", "RM3", "RM4", "RM4A", "RM4ab"]]
    for name in names:
        store.create_registered_model(name)

    # search with no filter should return all registered models
    rms, _ = _search_registered_models(store, None)
    assert rms == names

    # equality search using name should return exactly the 1 name
    rms, _ = _search_registered_models(store, "name='{}'".format(names[0]))
    assert rms == [names[0]]

    # equality search using name that is not valid should return nothing
    rms, _ = _search_registered_models(store, "name='{}'".format(names[0] + "cats"))
    assert rms == []

    # case-sensitive prefix search using LIKE should return all the RMs
    rms, _ = _search_registered_models(store, f"name LIKE '{prefix}%'")
    assert rms == names

    # case-sensitive prefix search using LIKE with surrounding % should return all the RMs
    rms, _ = _search_registered_models(store, "name LIKE '%RM%'")
    assert rms == names

    # case-sensitive prefix search using LIKE with surrounding % should return all the RMs
    # _e% matches test_for_search_ , so all RMs should match
    rms, _ = _search_registered_models(store, "name LIKE '_e%'")
    assert rms == names

    # case-sensitive prefix search using LIKE should return just rm4
    rms, _ = _search_registered_models(store, "name LIKE '{}%'".format(prefix + "RM4A"))
    assert rms == [names[4]]

    # case-sensitive prefix search using LIKE should return no models if no match
    rms, _ = _search_registered_models(store, "name LIKE '{}%'".format(prefix + "cats"))
    assert rms == []

    # confirm that LIKE is not case-sensitive
    rms, _ = _search_registered_models(store, "name lIkE '%blah%'")
    assert rms == []

    rms, _ = _search_registered_models(store, "name like '{}%'".format(prefix + "RM4A"))
    assert rms == [names[4]]

    # case-insensitive prefix search using ILIKE should return both rm5 and rm6
    rms, _ = _search_registered_models(store, "name ILIKE '{}%'".format(prefix + "RM4A"))
    assert rms == names[4:]

    # case-insensitive postfix search with ILIKE
    rms, _ = _search_registered_models(store, "name ILIKE '%RM4a%'")
    assert rms == names[4:]

    # case-insensitive prefix search using ILIKE should return both rm5 and rm6
    rms, _ = _search_registered_models(store, "name ILIKE '{}%'".format(prefix + "cats"))
    assert rms == []

    # confirm that ILIKE is not case-sensitive
    rms, _ = _search_registered_models(store, "name iLike '%blah%'")
    assert rms == []

    # confirm that ILIKE works for empty query
    rms, _ = _search_registered_models(store, "name iLike '%%'")
    assert rms == names

    rms, _ = _search_registered_models(store, "name ilike '%RM4a%'")
    assert rms == names[4:]

    # cannot search by invalid comparator types
    with pytest.raises(
        MlflowException,
        match="Parameter value is either not quoted or unidentified quote types used for "
        "string value something",
    ) as exception_context:
        _search_registered_models(store, "name!=something")
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    # cannot search by run_id
    with pytest.raises(
        MlflowException,
        match=r"Invalid attribute key 'run_id' specified. Valid keys are '{'name'}'",
    ) as exception_context:
        _search_registered_models(store, "run_id='%s'" % "somerunID")
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    # cannot search by source_path
    with pytest.raises(
        MlflowException,
        match=r"Invalid attribute key 'source_path' specified. Valid keys are '{'name'}'",
    ) as exception_context:
        _search_registered_models(store, "source_path = 'A/D'")
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    # cannot search by other params
    with pytest.raises(
        MlflowException, match=r"Invalid clause\(s\) in filter string"
    ) as exception_context:
        _search_registered_models(store, "evilhax = true")
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    # delete last registered model. search should not return the first 5
    store.delete_registered_model(name=names[-1])
    assert _search_registered_models(store, None, max_results=1000) == (names[:-1], None)

    # equality search using name should return no names
    assert _search_registered_models(store, "name='{}'".format(names[-1])) == ([], None)

    # case-sensitive prefix search using LIKE should return all the RMs
    assert _search_registered_models(store, f"name LIKE '{prefix}%'") == (
        names[0:5],
        None,
    )

    # case-insensitive prefix search using ILIKE should return both rm5 and rm6
    assert _search_registered_models(store, "name ILIKE '{}%'".format(prefix + "RM4A")) == (
        [names[4]],
        None,
    )


def test_search_registered_models_by_tag(store):
    name1 = "test_for_search_RM_by_tag1"
    name2 = "test_for_search_RM_by_tag2"
    tags1 = [
        RegisteredModelTag("t1", "abc"),
        RegisteredModelTag("t2", "xyz"),
    ]
    tags2 = [
        RegisteredModelTag("t1", "abcd"),
        RegisteredModelTag("t2", "xyz123"),
        RegisteredModelTag("t3", "XYZ"),
    ]
    store.create_registered_model(name1, tags1)
    store.create_registered_model(name2, tags2)

    rms, _ = _search_registered_models(store, "tag.t3 = 'XYZ'")
    assert rms == [name2]

    rms, _ = _search_registered_models(store, f"name = '{name1}' and tag.t1 = 'abc'")
    assert rms == [name1]

    rms, _ = _search_registered_models(store, "tag.t1 LIKE 'ab%'")
    assert rms == [name1, name2]

    rms, _ = _search_registered_models(store, "tag.t1 ILIKE 'aB%'")
    assert rms == [name1, name2]

    rms, _ = _search_registered_models(store, "tag.t1 LIKE 'ab%' AND tag.t2 LIKE 'xy%'")
    assert rms == [name1, name2]

    rms, _ = _search_registered_models(store, "tag.t3 = 'XYz'")
    assert rms == []

    rms, _ = _search_registered_models(store, "tag.T3 = 'XYZ'")
    assert rms == []

    rms, _ = _search_registered_models(store, "tag.t1 != 'abc'")
    assert rms == [name2]

    # test filter with duplicated keys
    rms, _ = _search_registered_models(store, "tag.t1 != 'abcd' and tag.t1 LIKE 'ab%'")
    assert rms == [name1]


def test_search_registered_models_order_by_simple(store):
    # create some registered models
    prefix = "test_for_search_"
    names = [prefix + name for name in ["RM1", "RM2", "RM3", "RM4", "RM4A", "RM4ab"]]
    for name in names:
        store.create_registered_model(name)
        time.sleep(0.001)  # sleep for windows store timestamp precision issues

    # by default order by name ASC
    rms, _ = _search_registered_models(store)
    assert rms == names

    # order by name DESC
    rms, _ = _search_registered_models(store, order_by=["name DESC"])
    assert rms == names[::-1]

    # order by last_updated_timestamp ASC
    store.update_registered_model(names[0], "latest updated")
    rms, _ = _search_registered_models(store, order_by=["last_updated_timestamp ASC"])
    assert rms[-1] == names[0]


def test_search_registered_model_pagination(store):
    rms = [store.create_registered_model(f"RM{i:03}").name for i in range(50)]

    # test flow with fixed max_results
    returned_rms = []
    query = "name LIKE 'RM%'"
    result, token = _search_registered_models(store, query, page_token=None, max_results=5)
    returned_rms.extend(result)
    while token:
        result, token = _search_registered_models(store, query, page_token=token, max_results=5)
        returned_rms.extend(result)
    assert rms == returned_rms

    # test that pagination will return all valid results in sorted order
    # by name ascending
    result, token1 = _search_registered_models(store, query, max_results=5)
    assert token1 is not None
    assert result == rms[0:5]

    result, token2 = _search_registered_models(store, query, page_token=token1, max_results=10)
    assert token2 is not None
    assert result == rms[5:15]

    result, token3 = _search_registered_models(store, query, page_token=token2, max_results=20)
    assert token3 is not None
    assert result == rms[15:35]

    result, token4 = _search_registered_models(store, query, page_token=token3, max_results=100)
    # assert that page token is None
    assert token4 is None
    assert result == rms[35:]

    # test that providing a completely invalid page token throws
    with pytest.raises(
        MlflowException, match=r"Invalid page token, could not base64-decode"
    ) as exception_context:
        _search_registered_models(store, query, page_token="evilhax", max_results=20)
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    # test that providing too large of a max_results throws
    with pytest.raises(
        MlflowException, match=r"Invalid value for max_results."
    ) as exception_context:
        _search_registered_models(store, query, page_token="evilhax", max_results=1e15)
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)


def test_search_registered_model_order_by(store):
    rms = []
    # explicitly mock the creation_timestamps because timestamps seem to be unstable in Windows
    for i in range(50):
        rms.append(store.create_registered_model(f"RM{i:03}").name)
        time.sleep(0.01)

    # test flow with fixed max_results and order_by (test stable order across pages)
    returned_rms = []
    query = "name LIKE 'RM%'"
    result, token = _search_registered_models(
        store, query, page_token=None, order_by=["name DESC"], max_results=5
    )
    returned_rms.extend(result)
    while token:
        result, token = _search_registered_models(
            store, query, page_token=token, order_by=["name DESC"], max_results=5
        )
        returned_rms.extend(result)
    # name descending should be the opposite order of the current order
    assert rms[::-1] == returned_rms
    # last_updated_timestamp descending should have the newest RMs first
    result, _ = _search_registered_models(
        store, query, page_token=None, order_by=["last_updated_timestamp DESC"], max_results=100
    )
    assert rms[::-1] == result
    # last_updated_timestamp ascending should have the oldest RMs first
    result, _ = _search_registered_models(
        store, query, page_token=None, order_by=["last_updated_timestamp ASC"], max_results=100
    )
    assert rms == result
    # name ascending should have the original order
    result, _ = _search_registered_models(
        store, query, page_token=None, order_by=["name ASC"], max_results=100
    )
    assert rms == result
    # test that no ASC/DESC defaults to ASC
    result, _ = _search_registered_models(
        store, query, page_token=None, order_by=["last_updated_timestamp"], max_results=100
    )
    assert rms == result
    with mock.patch("mlflow.store.model_registry.file_store.now", return_value=1):
        rm1 = store.create_registered_model("MR1").name
        rm2 = store.create_registered_model("MR2").name
    with mock.patch("mlflow.store.model_registry.file_store.now", return_value=2):
        rm3 = store.create_registered_model("MR3").name
        rm4 = store.create_registered_model("MR4").name
    query = "name LIKE 'MR%'"
    # test with multiple clauses
    result, _ = _search_registered_models(
        store,
        query,
        page_token=None,
        order_by=["last_updated_timestamp ASC", "name DESC"],
        max_results=100,
    )
    assert [rm2, rm1, rm4, rm3] == result
    # confirm that name ascending is the default, even if ties exist on other fields
    result, _ = _search_registered_models(
        store, query, page_token=None, order_by=[], max_results=100
    )
    assert [rm1, rm2, rm3, rm4] == result
    # test default tiebreak with descending timestamps
    result, _ = _search_registered_models(
        store, query, page_token=None, order_by=["last_updated_timestamp DESC"], max_results=100
    )
    assert [rm3, rm4, rm1, rm2] == result


def test_search_registered_model_order_by_errors(store):
    store.create_registered_model("dummy")
    query = "name LIKE 'RM%'"
    # test that invalid columns throw even if they come after valid columns
    with pytest.raises(
        MlflowException, match="Invalid attribute key 'description' specified."
    ) as exception_context:
        _search_registered_models(
            store,
            query,
            page_token=None,
            order_by=["name ASC", "description DESC"],
            max_results=5,
        )
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
    # test that invalid columns with random text throw even if they come after valid columns
    with pytest.raises(MlflowException, match=r"Invalid order_by clause '.+'") as exception_context:
        _search_registered_models(
            store,
            query,
            page_token=None,
            order_by=["name ASC", "last_updated_timestamp DESC blah"],
            max_results=5,
        )
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)


def test_set_model_version_tag(store):
    name1 = "SetModelVersionTag_TestMod"
    name2 = "SetModelVersionTag_TestMod 2"
    initial_tags = [
        ModelVersionTag("key", "value"),
        ModelVersionTag("anotherKey", "some other value"),
    ]
    store.create_registered_model(name1)
    store.create_registered_model(name2)
    run_id_1 = uuid.uuid4().hex
    run_id_2 = uuid.uuid4().hex
    run_id_3 = uuid.uuid4().hex
    store.create_model_version(name1, "A/B", run_id_1, initial_tags)
    store.create_model_version(name1, "A/C", run_id_2, initial_tags)
    store.create_model_version(name2, "A/D", run_id_3, initial_tags)
    new_tag = ModelVersionTag("randomTag", "not a random value")
    store.set_model_version_tag(name1, 1, new_tag)
    all_tags = initial_tags + [new_tag]
    rm1mv1 = store.get_model_version(name1, 1)
    assert rm1mv1.tags == {tag.key: tag.value for tag in all_tags}

    # test overriding a tag with the same key
    overriding_tag = ModelVersionTag("key", "overriding")
    store.set_model_version_tag(name1, 1, overriding_tag)
    all_tags = [tag for tag in all_tags if tag.key != "key"] + [overriding_tag]
    rm1mv1 = store.get_model_version(name1, 1)
    assert rm1mv1.tags == {tag.key: tag.value for tag in all_tags}
    # does not affect other model versions with the same key
    rm1mv2 = store.get_model_version(name1, 2)
    rm2mv1 = store.get_model_version(name2, 1)
    assert rm1mv2.tags == {tag.key: tag.value for tag in initial_tags}
    assert rm2mv1.tags == {tag.key: tag.value for tag in initial_tags}

    # can not set tag on deleted (non-existed) model version
    store.delete_model_version(name1, 2)
    with pytest.raises(
        MlflowException, match=rf"Model Version \(name={name1}, version=2\) not found"
    ) as exception_context:
        store.set_model_version_tag(name1, 2, overriding_tag)
    assert exception_context.value.error_code == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST)
    # test cannot set tags that are too long
    long_tag = ModelVersionTag("longTagKey", "a" * 5001)
    with pytest.raises(
        MlflowException,
        match=r"Model version value '.+' had length \d+, which exceeded length limit of 5000",
    ) as exception_context:
        store.set_model_version_tag(name1, 1, long_tag)
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
    # test can set tags that are somewhat long
    long_tag = ModelVersionTag("longTagKey", "a" * 4999)
    store.set_model_version_tag(name1, 1, long_tag)
    # can not set invalid tag
    with pytest.raises(MlflowException, match=r"Tag name cannot be None") as exception_context:
        store.set_model_version_tag(name2, 1, ModelVersionTag(key=None, value=""))
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
    # can not use invalid model name or version
    with pytest.raises(
        MlflowException, match=r"Registered model name cannot be empty"
    ) as exception_context:
        store.set_model_version_tag(None, 1, ModelVersionTag(key="key", value="value"))
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
    with pytest.raises(
        MlflowException, match=r"Model version must be an integer"
    ) as exception_context:
        store.set_model_version_tag(
            name2, "I am not a version", ModelVersionTag(key="key", value="value")
        )
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)


def test_delete_model_version_tag(store):

    name1 = "DeleteModelVersionTag_TestMod"
    name2 = "DeleteModelVersionTag_TestMod 2"
    initial_tags = [
        ModelVersionTag("key", "value"),
        ModelVersionTag("anotherKey", "some other value"),
    ]
    store.create_registered_model(name1)
    store.create_registered_model(name2)
    run_id_1 = uuid.uuid4().hex
    run_id_2 = uuid.uuid4().hex
    run_id_3 = uuid.uuid4().hex
    store.create_model_version(name1, "A/B", run_id_1, initial_tags)
    store.create_model_version(name1, "A/C", run_id_2, initial_tags)
    store.create_model_version(name2, "A/D", run_id_3, initial_tags)
    new_tag = ModelVersionTag("randomTag", "not a random value")
    store.set_model_version_tag(name1, 1, new_tag)
    store.delete_model_version_tag(name1, 1, "randomTag")
    rm1mv1 = store.get_model_version(name1, 1)
    assert rm1mv1.tags == {tag.key: tag.value for tag in initial_tags}

    # testing deleting a key does not affect other model versions with the same key
    store.delete_model_version_tag(name1, 1, "key")
    rm1mv1 = store.get_model_version(name1, 1)
    rm1mv2 = store.get_model_version(name1, 2)
    rm2mv1 = store.get_model_version(name2, 1)
    assert rm1mv1.tags == {"anotherKey": "some other value"}
    assert rm1mv2.tags == {tag.key: tag.value for tag in initial_tags}
    assert rm2mv1.tags == {tag.key: tag.value for tag in initial_tags}

    # delete tag that is already deleted does nothing
    store.delete_model_version_tag(name1, 1, "key")
    rm1mv1 = store.get_model_version(name1, 1)
    assert rm1mv1.tags == {"anotherKey": "some other value"}

    # can not delete tag on deleted (non-existed) model version
    store.delete_model_version(name2, 1)
    with pytest.raises(
        MlflowException, match=rf"Model Version \(name={name2}, version=1\) not found"
    ) as exception_context:
        store.delete_model_version_tag(name2, 1, "key")
    assert exception_context.value.error_code == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST)
    # can not delete tag with invalid key
    with pytest.raises(MlflowException, match=r"Tag name cannot be None") as exception_context:
        store.delete_model_version_tag(name1, 2, None)
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
    # can not use invalid model name or version
    with pytest.raises(
        MlflowException, match=r"Registered model name cannot be empty"
    ) as exception_context:
        store.delete_model_version_tag(None, 2, "key")
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
    with pytest.raises(
        MlflowException, match=r"Model version must be an integer"
    ) as exception_context:
        store.delete_model_version_tag(name1, "I am not a version", "key")
    assert exception_context.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)


def test_pyfunc_model_registry_with_file_store(store):
    import mlflow
    from mlflow.pyfunc import PythonModel

    class MyModel(PythonModel):
        def predict(self, context, model_input):
            return 7

    mlflow.set_registry_uri(path_to_local_file_uri(store.root_directory))
    with mlflow.start_run():
        mlflow.pyfunc.log_model(
            python_model=MyModel(), artifact_path="foo", registered_model_name="model1"
        )
        mlflow.pyfunc.log_model(
            python_model=MyModel(), artifact_path="foo", registered_model_name="model2"
        )
        mlflow.pyfunc.log_model(
            python_model=MyModel(), artifact_path="foo", registered_model_name="model1"
        )

    with mlflow.start_run():
        mlflow.log_param("A", "B")

    models = store.search_registered_models(max_results=10)
    assert len(models) == 2
    assert models[0].name == "model1"
    assert models[1].name == "model2"
    mv1 = store.search_model_versions("name = 'model1'")
    assert len(mv1) == 2 and mv1[0].name == "model1"
    mv2 = store.search_model_versions("name = 'model2'")
    assert len(mv2) == 1 and mv2[0].name == "model2"
