import os
import unittest

import mock
import tempfile
import uuid

from mlflow.utils.search_models_utils import SearchModelsUtils

import mlflow
import mlflow.db
import mlflow.store.db.base_sql_model
from mlflow.entities.model_registry import (
    RegisteredModel,
    ModelVersion,
    RegisteredModelTag,
    ModelVersionTag,
)
from mlflow.exceptions import MlflowException
from mlflow.protos.databricks_pb2 import (
    ErrorCode,
    RESOURCE_DOES_NOT_EXIST,
    INVALID_PARAMETER_VALUE,
    RESOURCE_ALREADY_EXISTS,
)
from mlflow.store.model_registry.sqlalchemy_store import SqlAlchemyStore
from tests.helper_functions import random_str

DB_URI = "sqlite:///"


class TestSqlAlchemyStoreSqlite(unittest.TestCase):
    def _get_store(self, db_uri=""):
        return SqlAlchemyStore(db_uri)

    def setUp(self):
        self.maxDiff = None  # print all differences on assert failures
        fd, self.temp_dbfile = tempfile.mkstemp()
        # Close handle immediately so that we can remove the file later on in Windows
        os.close(fd)
        self.db_url = "%s%s" % (DB_URI, self.temp_dbfile)
        self.store = self._get_store(self.db_url)

    def tearDown(self):
        mlflow.store.db.base_sql_model.Base.metadata.drop_all(self.store.engine)
        os.remove(self.temp_dbfile)

    def _rm_maker(self, name, tags=None, description=None):
        return self.store.create_registered_model(name, tags, description)

    def _mv_maker(
<<<<<<< HEAD
        self, name, source="path/to/source", run_id=uuid.uuid4().hex, tags=None, run_link=None,
=======
        self,
        name,
        source="path/to/source",
        run_id=uuid.uuid4().hex,
        tags=None,
        run_link=None,
        description=None,
>>>>>>> 3936705d... Add ability to add description in model/version create APIs (#3271)
    ):
        return self.store.create_model_version(
            name, source, run_id, tags, run_link=run_link, description=description
        )

    def _extract_latest_by_stage(self, latest_versions):
        return {mvd.current_stage: mvd.version for mvd in latest_versions}

    def test_create_registered_model(self):
        name = random_str() + "abCD"
        rm1 = self._rm_maker(name)
        self.assertEqual(rm1.name, name)
        self.assertEqual(rm1.description, None)

        # error on duplicate
        with self.assertRaises(MlflowException) as exception_context:
            self._rm_maker(name)
        assert exception_context.exception.error_code == ErrorCode.Name(RESOURCE_ALREADY_EXISTS)

        # slightly different name is ok
        for name2 in [name + "extra", name.lower(), name.upper(), name + name]:
            rm2 = self._rm_maker(name2)
            self.assertEqual(rm2.name, name2)

        # test create model with tags
        name2 = random_str() + "tags"
        tags = [
            RegisteredModelTag("key", "value"),
            RegisteredModelTag("anotherKey", "some other value"),
        ]
        rm2 = self._rm_maker(name2, tags)
        rmd2 = self.store.get_registered_model(name2)
        self.assertEqual(rm2.name, name2)
        self.assertEqual(rm2.tags, {tag.key: tag.value for tag in tags})
        self.assertEqual(rmd2.name, name2)
        self.assertEqual(rmd2.tags, {tag.key: tag.value for tag in tags})

        # create with description
        name3 = random_str() + "-description"
        description = "the best model ever"
        rm3 = self._rm_maker(name3, description=description)
        rmd3 = self.store.get_registered_model(name3)
        self.assertEqual(rm3.name, name3)
        self.assertEqual(rm3.description, description)
        self.assertEqual(rmd3.name, name3)
        self.assertEqual(rmd3.description, description)

        # invalid model name will fail
        with self.assertRaises(MlflowException) as exception_context:
            self._rm_maker(None)
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
        with self.assertRaises(MlflowException) as exception_context:
            self._rm_maker("")
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    def test_get_registered_model(self):
        name = "model_1"
        tags = [
            RegisteredModelTag("key", "value"),
            RegisteredModelTag("anotherKey", "some other value"),
        ]
        # use fake clock
        with mock.patch("time.time") as mock_time:
            mock_time.return_value = 1234
            rm = self._rm_maker(name, tags)
            self.assertEqual(rm.name, name)
        rmd = self.store.get_registered_model(name=name)
        self.assertEqual(rmd.name, name)
        self.assertEqual(rmd.creation_timestamp, 1234000)
        self.assertEqual(rmd.last_updated_timestamp, 1234000)
        self.assertEqual(rmd.description, None)
        self.assertEqual(rmd.latest_versions, [])
        self.assertEqual(rmd.tags, {tag.key: tag.value for tag in tags})

    def test_update_registered_model(self):
        name = "model_for_update_RM"
        rm1 = self._rm_maker(name)
        rmd1 = self.store.get_registered_model(name=name)
        self.assertEqual(rm1.name, name)
        self.assertEqual(rmd1.description, None)

        # update description
        rm2 = self.store.update_registered_model(name=name, description="test model")
        rmd2 = self.store.get_registered_model(name=name)
        self.assertEqual(rm2.name, "model_for_update_RM")
        self.assertEqual(rmd2.name, "model_for_update_RM")
        self.assertEqual(rmd2.description, "test model")

    def test_rename_registered_model(self):
        original_name = "original name"
        new_name = "new name"
        self._rm_maker(original_name)
        self._mv_maker(original_name)
        self._mv_maker(original_name)
        rm = self.store.get_registered_model(original_name)
        mv1 = self.store.get_model_version(original_name, 1)
        mv2 = self.store.get_model_version(original_name, 2)
        self.assertEqual(rm.name, original_name)
        self.assertEqual(mv1.name, original_name)
        self.assertEqual(mv2.name, original_name)

        # test renaming registered model also updates its model versions
        self.store.rename_registered_model(original_name, new_name)
        rm = self.store.get_registered_model(new_name)
        mv1 = self.store.get_model_version(new_name, 1)
        mv2 = self.store.get_model_version(new_name, 2)
        self.assertEqual(rm.name, new_name)
        self.assertEqual(mv1.name, new_name)
        self.assertEqual(mv2.name, new_name)

        # test accessing the model with the old name will fail
        with self.assertRaises(MlflowException) as exception_context:
            self.store.get_registered_model(original_name)
        assert exception_context.exception.error_code == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST)

        # test name another model with the replaced name is ok
        self._rm_maker(original_name)
        # cannot rename model to conflict with an existing model
        with self.assertRaises(MlflowException) as exception_context:
            self.store.rename_registered_model(new_name, original_name)
        assert exception_context.exception.error_code == ErrorCode.Name(RESOURCE_ALREADY_EXISTS)
        # invalid model name will fail
        with self.assertRaises(MlflowException) as exception_context:
            self.store.rename_registered_model(original_name, None)
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
        with self.assertRaises(MlflowException) as exception_context:
            self.store.rename_registered_model(original_name, "")
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    def test_delete_registered_model(self):
        name = "model_for_delete_RM"
        self._rm_maker(name)
        self._mv_maker(name)
        rm1 = self.store.get_registered_model(name=name)
        mv1 = self.store.get_model_version(name, 1)
        self.assertEqual(rm1.name, name)
        self.assertEqual(mv1.name, name)

        # delete model
        self.store.delete_registered_model(name=name)

        # cannot get model
        with self.assertRaises(MlflowException) as exception_context:
            self.store.get_registered_model(name=name)
        assert exception_context.exception.error_code == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST)

        # cannot update a delete model
        with self.assertRaises(MlflowException) as exception_context:
            self.store.update_registered_model(name=name, description="deleted")
        assert exception_context.exception.error_code == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST)

        # cannot delete it again
        with self.assertRaises(MlflowException) as exception_context:
            self.store.delete_registered_model(name=name)
        assert exception_context.exception.error_code == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST)

        # model versions are cascade deleted with the registered model
        with self.assertRaises(MlflowException) as exception_context:
            self.store.get_model_version(name, 1)
        assert exception_context.exception.error_code == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST)

    def _list_registered_models(self, page_token=None, max_results=10):
        result = self.store.list_registered_models(max_results, page_token)
        for idx in range(len(result)):
            result[idx] = result[idx].name
        return result

    def test_list_registered_model(self):
        self._rm_maker("A")
        registered_models = self.store.list_registered_models(max_results=10, page_token=None)
        self.assertEqual(len(registered_models), 1)
        self.assertEqual(registered_models[0].name, "A")
        self.assertIsInstance(registered_models[0], RegisteredModel)

        self._rm_maker("B")
        self.assertEqual(set(self._list_registered_models()), set(["A", "B"]))

        self._rm_maker("BB")
        self._rm_maker("BA")
        self._rm_maker("AB")
        self._rm_maker("BBC")
        self.assertEqual(
            set(self._list_registered_models()), set(["A", "B", "BB", "BA", "AB", "BBC"]),
        )

        # list should not return deleted models
        self.store.delete_registered_model(name="BA")
        self.store.delete_registered_model(name="B")
        self.assertEqual(set(self._list_registered_models()), set(["A", "BB", "AB", "BBC"]))

    def test_list_registered_model_paginated_last_page(self):
        rms = [self._rm_maker("RM{:03}".format(i)).name for i in range(50)]

        # test flow with fixed max_results
        returned_rms = []
        result = self._list_registered_models(page_token=None, max_results=25)
        returned_rms.extend(result)
        while result.token:
            result = self._list_registered_models(page_token=result.token, max_results=25)
            self.assertEqual(len(result), 25)
            returned_rms.extend(result)
        self.assertEqual(result.token, None)
        self.assertEqual(set(rms), set(returned_rms))

    def test_list_registered_model_paginated_returns_in_correct_order(self):
        rms = [self._rm_maker("RM{:03}".format(i)).name for i in range(50)]

        # test that pagination will return all valid results in sorted order
        # by name ascending
        result = self._list_registered_models(max_results=5)
        self.assertNotEqual(result.token, None)
        self.assertEqual(result, rms[0:5])

        result = self._list_registered_models(page_token=result.token, max_results=10)
        self.assertNotEqual(result.token, None)
        self.assertEqual(result, rms[5:15])

        result = self._list_registered_models(page_token=result.token, max_results=20)
        self.assertNotEqual(result.token, None)
        self.assertEqual(result, rms[15:35])

        result = self._list_registered_models(page_token=result.token, max_results=100)
        # assert that page token is None
        self.assertEqual(result.token, None)
        self.assertEqual(result, rms[35:])

    def test_list_registered_model_paginated_errors(self):
        rms = [self._rm_maker("RM{:03}".format(i)).name for i in range(50)]
        # test that providing a completely invalid page token throws
        with self.assertRaises(MlflowException) as exception_context:
            self._list_registered_models(page_token="evilhax", max_results=20)
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

        # test that providing too large of a max_results throws
        with self.assertRaises(MlflowException) as exception_context:
            self._list_registered_models(page_token="evilhax", max_results=1e15)
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
        self.assertIn(
            "Invalid value for request parameter max_results", exception_context.exception.message,
        )
        # list should not return deleted models
        self.store.delete_registered_model(name="RM{0:03}".format(0))
        self.assertEqual(set(self._list_registered_models(max_results=100)), set(rms[1:]))

    def test_get_latest_versions(self):
        name = "test_for_latest_versions"
        self._rm_maker(name)
        rmd1 = self.store.get_registered_model(name=name)
        self.assertEqual(rmd1.latest_versions, [])

        mv1 = self._mv_maker(name)
        self.assertEqual(mv1.version, 1)
        rmd2 = self.store.get_registered_model(name=name)
        self.assertEqual(self._extract_latest_by_stage(rmd2.latest_versions), {"None": 1})

        # add a bunch more
        mv2 = self._mv_maker(name)
        self.assertEqual(mv2.version, 2)
        self.store.transition_model_version_stage(
            name=mv2.name, version=mv2.version, stage="Production", archive_existing_versions=False,
        )

        mv3 = self._mv_maker(name)
        self.assertEqual(mv3.version, 3)
        self.store.transition_model_version_stage(
            name=mv3.name, version=mv3.version, stage="Production", archive_existing_versions=False,
        )
        mv4 = self._mv_maker(name)
        self.assertEqual(mv4.version, 4)
        self.store.transition_model_version_stage(
            name=mv4.name, version=mv4.version, stage="Staging", archive_existing_versions=False,
        )

        # test that correct latest versions are returned for each stage
        rmd4 = self.store.get_registered_model(name=name)
        self.assertEqual(
            self._extract_latest_by_stage(rmd4.latest_versions),
            {"None": 1, "Production": 3, "Staging": 4},
        )

        # delete latest Production, and should point to previous one
        self.store.delete_model_version(name=mv3.name, version=mv3.version)
        rmd5 = self.store.get_registered_model(name=name)
        self.assertEqual(
            self._extract_latest_by_stage(rmd5.latest_versions),
            {"None": 1, "Production": 2, "Staging": 4},
        )

    def test_set_registered_model_tag(self):
        name1 = "SetRegisteredModelTag_TestMod"
        name2 = "SetRegisteredModelTag_TestMod 2"
        initial_tags = [
            RegisteredModelTag("key", "value"),
            RegisteredModelTag("anotherKey", "some other value"),
        ]
        self._rm_maker(name1, initial_tags)
        self._rm_maker(name2, initial_tags)
        new_tag = RegisteredModelTag("randomTag", "not a random value")
        self.store.set_registered_model_tag(name1, new_tag)
        rm1 = self.store.get_registered_model(name=name1)
        all_tags = initial_tags + [new_tag]
        self.assertEqual(rm1.tags, {tag.key: tag.value for tag in all_tags})

        # test overriding a tag with the same key
        overriding_tag = RegisteredModelTag("key", "overriding")
        self.store.set_registered_model_tag(name1, overriding_tag)
        all_tags = [tag for tag in all_tags if tag.key != "key"] + [overriding_tag]
        rm1 = self.store.get_registered_model(name=name1)
        self.assertEqual(rm1.tags, {tag.key: tag.value for tag in all_tags})
        # does not affect other models with the same key
        rm2 = self.store.get_registered_model(name=name2)
        self.assertEqual(rm2.tags, {tag.key: tag.value for tag in initial_tags})

        # can not set tag on deleted (non-existed) registered model
        self.store.delete_registered_model(name1)
        with self.assertRaises(MlflowException) as exception_context:
            self.store.set_registered_model_tag(name1, overriding_tag)
        assert exception_context.exception.error_code == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST)
        # test cannot set tags that are too long
        long_tag = RegisteredModelTag("longTagKey", "a" * 5001)
        with self.assertRaises(MlflowException) as exception_context:
            self.store.set_registered_model_tag(name2, long_tag)
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
        # test can set tags that are somewhat long
        long_tag = RegisteredModelTag("longTagKey", "a" * 4999)
        self.store.set_registered_model_tag(name2, long_tag)
        # can not set invalid tag
        with self.assertRaises(MlflowException) as exception_context:
            self.store.set_registered_model_tag(name2, RegisteredModelTag(key=None, value=""))
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
        # can not use invalid model name
        with self.assertRaises(MlflowException) as exception_context:
            self.store.set_registered_model_tag(None, RegisteredModelTag(key="key", value="value"))
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    def test_delete_registered_model_tag(self):
        name1 = "DeleteRegisteredModelTag_TestMod"
        name2 = "DeleteRegisteredModelTag_TestMod 2"
        initial_tags = [
            RegisteredModelTag("key", "value"),
            RegisteredModelTag("anotherKey", "some other value"),
        ]
        self._rm_maker(name1, initial_tags)
        self._rm_maker(name2, initial_tags)
        new_tag = RegisteredModelTag("randomTag", "not a random value")
        self.store.set_registered_model_tag(name1, new_tag)
        self.store.delete_registered_model_tag(name1, "randomTag")
        rm1 = self.store.get_registered_model(name=name1)
        self.assertEqual(rm1.tags, {tag.key: tag.value for tag in initial_tags})

        # testing deleting a key does not affect other models with the same key
        self.store.delete_registered_model_tag(name1, "key")
        rm1 = self.store.get_registered_model(name=name1)
        rm2 = self.store.get_registered_model(name=name2)
        self.assertEqual(rm1.tags, {"anotherKey": "some other value"})
        self.assertEqual(rm2.tags, {tag.key: tag.value for tag in initial_tags})

        # delete tag that is already deleted does nothing
        self.store.delete_registered_model_tag(name1, "key")
        rm1 = self.store.get_registered_model(name=name1)
        self.assertEqual(rm1.tags, {"anotherKey": "some other value"})

        # can not delete tag on deleted (non-existed) registered model
        self.store.delete_registered_model(name1)
        with self.assertRaises(MlflowException) as exception_context:
            self.store.delete_registered_model_tag(name1, "anotherKey")
        assert exception_context.exception.error_code == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST)
        # can not delete tag with invalid key
        with self.assertRaises(MlflowException) as exception_context:
            self.store.delete_registered_model_tag(name2, None)
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
        # can not use invalid model name
        with self.assertRaises(MlflowException) as exception_context:
            self.store.delete_registered_model_tag(None, "key")
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    def test_create_model_version(self):
        name = "test_for_update_MV"
        self._rm_maker(name)
        run_id = uuid.uuid4().hex
        with mock.patch("time.time") as mock_time:
            mock_time.return_value = 456778
            mv1 = self._mv_maker(name, "a/b/CD", run_id)
            self.assertEqual(mv1.name, name)
            self.assertEqual(mv1.version, 1)

        mvd1 = self.store.get_model_version(mv1.name, mv1.version)
        self.assertEqual(mvd1.name, name)
        self.assertEqual(mvd1.version, 1)
        self.assertEqual(mvd1.current_stage, "None")
        self.assertEqual(mvd1.creation_timestamp, 456778000)
        self.assertEqual(mvd1.last_updated_timestamp, 456778000)
        self.assertEqual(mvd1.description, None)
        self.assertEqual(mvd1.source, "a/b/CD")
        self.assertEqual(mvd1.run_id, run_id)
        self.assertEqual(mvd1.status, "READY")
        self.assertEqual(mvd1.status_message, None)
        self.assertEqual(mvd1.tags, {})

        # new model versions for same name autoincrement versions
        mv2 = self._mv_maker(name)
        mvd2 = self.store.get_model_version(name=mv2.name, version=mv2.version)
        self.assertEqual(mv2.version, 2)
        self.assertEqual(mvd2.version, 2)

        # create model version with tags return model version entity with tags
        tags = [
            ModelVersionTag("key", "value"),
            ModelVersionTag("anotherKey", "some other value"),
        ]
        mv3 = self._mv_maker(name, tags=tags)
        mvd3 = self.store.get_model_version(name=mv3.name, version=mv3.version)
        self.assertEqual(mv3.version, 3)
        self.assertEqual(mv3.tags, {tag.key: tag.value for tag in tags})
        self.assertEqual(mvd3.version, 3)
        self.assertEqual(mvd3.tags, {tag.key: tag.value for tag in tags})

        # create model versions with runLink
        run_link = "http://localhost:3000/path/to/run/"
        mv4 = self._mv_maker(name, run_link=run_link)
        mvd4 = self.store.get_model_version(name, mv4.version)
        self.assertEqual(mv4.version, 4)
        self.assertEqual(mv4.run_link, run_link)
        self.assertEqual(mvd4.version, 4)
        self.assertEqual(mvd4.run_link, run_link)

        # create model version with description
        description = "the best model ever"
        mv5 = self._mv_maker(name, description=description)
        mvd5 = self.store.get_model_version(name, mv5.version)
        self.assertEqual(mv5.version, 5)
        self.assertEqual(mv5.description, description)
        self.assertEqual(mvd5.version, 5)
        self.assertEqual(mvd5.description, description)

    def test_update_model_version(self):
        name = "test_for_update_MV"
        self._rm_maker(name)
        mv1 = self._mv_maker(name)
        mvd1 = self.store.get_model_version(name=mv1.name, version=mv1.version)
        self.assertEqual(mvd1.name, name)
        self.assertEqual(mvd1.version, 1)
        self.assertEqual(mvd1.current_stage, "None")

        # update stage
        self.store.transition_model_version_stage(
            name=mv1.name, version=mv1.version, stage="Production", archive_existing_versions=False,
        )
        mvd2 = self.store.get_model_version(name=mv1.name, version=mv1.version)
        self.assertEqual(mvd2.name, name)
        self.assertEqual(mvd2.version, 1)
        self.assertEqual(mvd2.current_stage, "Production")
        self.assertEqual(mvd2.description, None)

        # update description
        self.store.update_model_version(
            name=mv1.name, version=mv1.version, description="test model version"
        )
        mvd3 = self.store.get_model_version(name=mv1.name, version=mv1.version)
        self.assertEqual(mvd3.name, name)
        self.assertEqual(mvd3.version, 1)
        self.assertEqual(mvd3.current_stage, "Production")
        self.assertEqual(mvd3.description, "test model version")

        # only valid stages can be set
        with self.assertRaises(MlflowException) as exception_context:
            self.store.transition_model_version_stage(
                mv1.name, mv1.version, stage="unknown", archive_existing_versions=False
            )
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

        # stages are case-insensitive and auto-corrected to system stage names
        for stage_name in ["STAGING", "staging", "StAgInG"]:
            self.store.transition_model_version_stage(
                name=mv1.name,
                version=mv1.version,
                stage=stage_name,
                archive_existing_versions=False,
            )
            mvd5 = self.store.get_model_version(name=mv1.name, version=mv1.version)
            self.assertEqual(mvd5.current_stage, "Staging")

    def test_transition_model_version_stage_when_archive_existing_versions_is_false(self,):
        name = "model"
        self._rm_maker(name)
        mv1 = self._mv_maker(name)
        mv2 = self._mv_maker(name)
        mv3 = self._mv_maker(name)

        # test that when `archive_existing_versions` is False, transitioning a model version
        # to the inactive stages ("Archived" and "None") does not throw.
        for stage in ["Archived", "None"]:
            self.store.transition_model_version_stage(name, mv1.version, stage, False)

        self.store.transition_model_version_stage(name, mv1.version, "Staging", False)
        self.store.transition_model_version_stage(name, mv2.version, "Production", False)
        self.store.transition_model_version_stage(name, mv3.version, "Staging", False)

        mvd1 = self.store.get_model_version(name=name, version=mv1.version)
        mvd2 = self.store.get_model_version(name=name, version=mv2.version)
        mvd3 = self.store.get_model_version(name=name, version=mv3.version)

        self.assertEqual(mvd1.current_stage, "Staging")
        self.assertEqual(mvd2.current_stage, "Production")
        self.assertEqual(mvd3.current_stage, "Staging")

        self.store.transition_model_version_stage(name, mv3.version, "Production", False)

        mvd1 = self.store.get_model_version(name=name, version=mv1.version)
        mvd2 = self.store.get_model_version(name=name, version=mv2.version)
        mvd3 = self.store.get_model_version(name=name, version=mv3.version)

        self.assertEqual(mvd1.current_stage, "Staging")
        self.assertEqual(mvd2.current_stage, "Production")
        self.assertEqual(mvd3.current_stage, "Production")

    def test_transition_model_version_stage_when_archive_existing_versions_is_true(self,):
        name = "model"
        self._rm_maker(name)
        mv1 = self._mv_maker(name)
        mv2 = self._mv_maker(name)
        mv3 = self._mv_maker(name)

        msg = (
            r"Model version transition cannot archive existing model versions "
            r"because .+ is not an Active stage. Valid stages are .+"
        )

        # test that when `archive_existing_versions` is True, transitioning a model version
        # to the inactive stages ("Archived" and "None") throws.
        for stage in ["Archived", "None"]:
            with self.assertRaisesRegex(MlflowException, msg):
                self.store.transition_model_version_stage(name, mv1.version, stage, True)

        self.store.transition_model_version_stage(name, mv1.version, "Staging", False)
        self.store.transition_model_version_stage(name, mv2.version, "Production", False)
        self.store.transition_model_version_stage(name, mv3.version, "Staging", True)

        mvd1 = self.store.get_model_version(name=name, version=mv1.version)
        mvd2 = self.store.get_model_version(name=name, version=mv2.version)
        mvd3 = self.store.get_model_version(name=name, version=mv3.version)

        self.assertEqual(mvd1.current_stage, "Archived")
        self.assertEqual(mvd2.current_stage, "Production")
        self.assertEqual(mvd3.current_stage, "Staging")
        self.assertEqual(mvd1.last_updated_timestamp, mvd3.last_updated_timestamp)

        self.store.transition_model_version_stage(name, mv3.version, "Production", True)

        mvd1 = self.store.get_model_version(name=name, version=mv1.version)
        mvd2 = self.store.get_model_version(name=name, version=mv2.version)
        mvd3 = self.store.get_model_version(name=name, version=mv3.version)

        self.assertEqual(mvd1.current_stage, "Archived")
        self.assertEqual(mvd2.current_stage, "Archived")
        self.assertEqual(mvd3.current_stage, "Production")
        self.assertEqual(mvd2.last_updated_timestamp, mvd3.last_updated_timestamp)

    def test_delete_model_version(self):
        name = "test_for_delete_MV"
        initial_tags = [
            ModelVersionTag("key", "value"),
            ModelVersionTag("anotherKey", "some other value"),
        ]
        self._rm_maker(name)
        mv = self._mv_maker(name, tags=initial_tags)
        mvd = self.store.get_model_version(name=mv.name, version=mv.version)
        self.assertEqual(mvd.name, name)

        self.store.delete_model_version(name=mv.name, version=mv.version)

        # cannot get a deleted model version
        with self.assertRaises(MlflowException) as exception_context:
            self.store.get_model_version(name=mv.name, version=mv.version)
        assert exception_context.exception.error_code == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST)

        # cannot update a delete
        with self.assertRaises(MlflowException) as exception_context:
            self.store.update_model_version(mv.name, mv.version, description="deleted!")
        assert exception_context.exception.error_code == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST)

        # cannot delete it again
        with self.assertRaises(MlflowException) as exception_context:
            self.store.delete_model_version(name=mv.name, version=mv.version)
        assert exception_context.exception.error_code == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST)

    def test_delete_model_version_redaction(self):
        name = "test_for_delete_MV_redaction"
        run_link = "http://localhost:5000/path/to/run"
        run_id = "12345"
        source = "path/to/source"
        self._rm_maker(name)
        mv = self._mv_maker(name, source=source, run_id=run_id, run_link=run_link)
        mvd = self.store.get_model_version(name=name, version=mv.version)
        self.assertEqual(mvd.run_link, run_link)
        self.assertEqual(mvd.run_id, run_id)
        self.assertEqual(mvd.source, source)
        # delete the MV now
        self.store.delete_model_version(name, mv.version)
        # verify that the relevant fields are redacted
        mvd_deleted = self.store._get_sql_model_version_including_deleted(
            name=name, version=mv.version
        )
        self.assertIn("REDACTED", mvd_deleted.run_link)
        self.assertIn("REDACTED", mvd_deleted.source)
        self.assertIn("REDACTED", mvd_deleted.run_id)

    def test_get_model_version_download_uri(self):
        name = "test_for_update_MV"
        self._rm_maker(name)
        source_path = "path/to/source"
        mv = self._mv_maker(name, source=source_path, run_id=uuid.uuid4().hex)
        mvd1 = self.store.get_model_version(name=mv.name, version=mv.version)
        self.assertEqual(mvd1.name, name)
        self.assertEqual(mvd1.source, source_path)

        # download location points to source
        self.assertEqual(
            self.store.get_model_version_download_uri(name=mv.name, version=mv.version),
            source_path,
        )

        # download URI does not change even if model version is updated
        self.store.transition_model_version_stage(
            name=mv.name, version=mv.version, stage="Production", archive_existing_versions=False,
        )
        self.store.update_model_version(
            name=mv.name, version=mv.version, description="Test for Path"
        )
        mvd2 = self.store.get_model_version(name=mv.name, version=mv.version)
        self.assertEqual(mvd2.source, source_path)
        self.assertEqual(
            self.store.get_model_version_download_uri(name=mv.name, version=mv.version),
            source_path,
        )

        # cannot retrieve download URI for deleted model versions
        self.store.delete_model_version(name=mv.name, version=mv.version)
        with self.assertRaises(MlflowException) as exception_context:
            self.store.get_model_version_download_uri(name=mv.name, version=mv.version)
        assert exception_context.exception.error_code == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST)

    def test_search_model_versions(self):
        # create some model versions
        name = "test_for_search_MV"
        self._rm_maker(name)
        run_id_1 = uuid.uuid4().hex
        run_id_2 = uuid.uuid4().hex
        run_id_3 = uuid.uuid4().hex
        mv1 = self._mv_maker(name=name, source="A/B", run_id=run_id_1)
        self.assertEqual(mv1.version, 1)
        mv2 = self._mv_maker(name=name, source="A/C", run_id=run_id_2)
        self.assertEqual(mv2.version, 2)
        mv3 = self._mv_maker(name=name, source="A/D", run_id=run_id_2)
        self.assertEqual(mv3.version, 3)
        mv4 = self._mv_maker(name=name, source="A/D", run_id=run_id_3)
        self.assertEqual(mv4.version, 4)

        def search_versions(filter_string):
            return [mvd.version for mvd in self.store.search_model_versions(filter_string)]

        # search using name should return all 4 versions
        self.assertEqual(set(search_versions("name='%s'" % name)), set([1, 2, 3, 4]))

        # search using run_id_1 should return version 1
        self.assertEqual(set(search_versions("run_id='%s'" % run_id_1)), set([1]))

        # search using run_id_2 should return versions 2 and 3
        self.assertEqual(set(search_versions("run_id='%s'" % run_id_2)), set([2, 3]))

        # search using source_path "A/D" should return version 3 and 4
        self.assertEqual(set(search_versions("source_path = 'A/D'")), set([3, 4]))

        # search using source_path "A" should not return anything
        self.assertEqual(len(search_versions("source_path = 'A'")), 0)
        self.assertEqual(len(search_versions("source_path = 'A/'")), 0)
        self.assertEqual(len(search_versions("source_path = ''")), 0)

        # delete mv4. search should not return version 4
        self.store.delete_model_version(name=mv4.name, version=mv4.version)
        self.assertEqual(set(search_versions("")), set([1, 2, 3]))

        self.assertEqual(set(search_versions(None)), set([1, 2, 3]))

        self.assertEqual(set(search_versions("name='%s'" % name)), set([1, 2, 3]))

        self.assertEqual(set(search_versions("source_path = 'A/D'")), set([3]))

        self.store.transition_model_version_stage(
            name=mv1.name, version=mv1.version, stage="production", archive_existing_versions=False,
        )

        self.store.update_model_version(
            name=mv1.name, version=mv1.version, description="Online prediction model!"
        )

        mvds = self.store.search_model_versions("run_id = '%s'" % run_id_1)
        assert 1 == len(mvds)
        assert isinstance(mvds[0], ModelVersion)
        assert mvds[0].current_stage == "Production"
        assert mvds[0].run_id == run_id_1
        assert mvds[0].source == "A/B"
        assert mvds[0].description == "Online prediction model!"

    def _search_registered_models(
        self, filter_string, max_results=10, order_by=None, page_token=None
    ):
        result = self.store.search_registered_models(
            filter_string=filter_string,
            max_results=max_results,
            order_by=order_by,
            page_token=page_token,
        )
        return [registered_model.name for registered_model in result], result.token

    def test_search_registered_models_attributes(self):
        def test_all_attribute_filter(attribute_filter, expected_rms):
            for attribute_filter_string in [
                attribute_filter,
                "attribute." + attribute_filter,
                "attr." + attribute_filter,
                "model" + attribute_filter,
                "registered_model" + attribute_filter,
                "models" + attribute_filter,
                "registered_models" + attribute_filter,
            ]:
                result_rms, _ = self._search_registered_models(attribute_filter_string)
                self.assertEqual(result_rms, expected_rms)

        # create some registered models
        prefix = "test_for_search_"
        names = [prefix + name for name in ["RM1", "RM2", "RM3", "RM4", "RM4A", "RM4a"]]
        for name in names:
            self._rm_maker(name)

        # search with no filter should return all registered models
        rms, _ = self._search_registered_models(None)
        self.assertEqual(rms, names)

        # equality search using name should return exactly the 1 name
        test_all_attribute_filter("name='{}'".format(names[0]), [names[0]])

        # equality search using name that is not valid should return nothing
        test_all_attribute_filter("name='{}'".format(names[0] + "cats"), [])

        # case-sensitive prefix search using LIKE should return all the RMs
        test_all_attribute_filter("name LIKE '{}%'".format(prefix), names)

        # case-sensitive prefix search using LIKE with surrounding % should return all the RMs
        test_all_attribute_filter("name LIKE '%RM%'", names)

        # case-sensitive prefix search using LIKE with surrounding % should return all the RMs
        # _e% matches test_for_search_ , so all RMs should match
        test_all_attribute_filter("name LIKE '_e%'", names)

        # case-sensitive prefix search using LIKE should return just rm4
        test_all_attribute_filter("name LIKE '{}%'".format(prefix + "RM4A"), [names[4]])

        # case-sensitive prefix search using LIKE should return no models if no match
        test_all_attribute_filter("name LIKE '{}%'".format(prefix + "cats"), [])

        # confirm that LIKE is not case-sensitive
        test_all_attribute_filter("name lIkE '%blah%'", [])
        test_all_attribute_filter("name like '{}%'".format(prefix + "RM4A"), [names[4]])

        # case-insensitive prefix search using ILIKE should return both rm5 and rm6
        test_all_attribute_filter("name ILIKE '{}%'".format(prefix + "RM4A"), names[4:])

        # case-insensitive postfix search with ILIKE
        test_all_attribute_filter("name ILIKE '%RM4a'", names[4:])

        # case-insensitive prefix search using ILIKE should return both rm5 and rm6
        test_all_attribute_filter("name ILIKE '{}%'".format(prefix + "cats"), [])

        # confirm that ILIKE is not case-sensitive
        test_all_attribute_filter("name iLike '%blah%'", [])

        # confirm that ILIKE works for empty query
        test_all_attribute_filter("name iLike '%%'", names)

        test_all_attribute_filter("name ilike '%RM4a'", names[4:])

        # test 'and' clause
        rms, _ = self._search_registered_models("name LIKE '%RM%' and attr.name != 'RM'")
        self.assertEqual(rms, names)

        rms, _ = self._search_registered_models(
            "attribute.name = '{}RM2' and name ilike '%rm%'".format(prefix)
        )
        self.assertEqual(rms, [names[1]])

        for bad_filter_string in [
            "name!=something",
            "run_id='%s'" % "somerunID",
            "source_path = 'A/D'",
            "evilhax = true",
        ]:
            for bad_attribute_filter in [
                bad_filter_string,
                "attribute." + bad_filter_string,
                "attr." + bad_filter_string,
            ]:
                with self.assertRaises(MlflowException) as exception_context:
                    self._search_registered_models(bad_attribute_filter)
                print(exception_context.exception.error_code)
                print(exception_context.exception.message)
                assert exception_context.exception.error_code == ErrorCode.Name(
                    INVALID_PARAMETER_VALUE
                )

        # delete last registered model. search should not return the first 5
        self.store.delete_registered_model(name=names[-1])
        self.assertEqual(self._search_registered_models(None, max_results=1000), (names[:-1], None))

        # equality search using name should return no names
        self.assertEqual(self._search_registered_models("name='{}'".format(names[-1])), ([], None))

        # case-sensitive prefix search using LIKE should return all the RMs
        self.assertEqual(
            self._search_registered_models("name LIKE '{}%'".format(prefix)), (names[0:5], None),
        )

        # case-insensitive prefix search using ILIKE should return both rm5 and rm6
        self.assertEqual(
            self._search_registered_models("name ILIKE '{}%'".format(prefix + "RM4A")),
            ([names[4]], None),
        )

    def test_bad_comparators_for_registered_model(self):
        for entity_type in ["tags", "attributes"]:
            for bad_comparator in [">", "<", ">=", "<=", "~"]:
                key = "name"
                entity_value = "'abc'"
                if not entity_type:
                    bad_filter = "{key} {comparator} {value}".format(
                        key=key, comparator=bad_comparator, value=entity_value
                    )
                else:
                    bad_filter = "{entity_type}.{key} {comparator} {value}".format(
                        entity_type=entity_type,
                        key=key,
                        comparator=bad_comparator,
                        value=entity_value,
                    )
                with self.assertRaises(MlflowException) as exception_context:
                    self._search_registered_models(bad_filter)
                assert exception_context.exception.error_code == ErrorCode.Name(
                    INVALID_PARAMETER_VALUE
                )

    def _set_up_model_and_tags_for_search(self, prefix):
        # create some registered models
        names = [prefix + name for name in ["RM1", "RM2", "RM3", "RM4", "RM4A", "RM4a"]]
        for name in names:
            self._rm_maker(name)
        names_subset1 = [prefix + name for name in ["RM1", "RM2", "RM3", "RM4"]]
        for name in names_subset1:
            self.store.set_registered_model_tag(
                name, RegisteredModelTag("training algorithm", "lightgbm")
            )
        names_subset2 = [prefix + name for name in ["RM4A", "RM4a"]]
        for name in names_subset2:
            self.store.set_registered_model_tag(
                name, RegisteredModelTag("training algorithm", "xgboost")
            )
        # set registered model tags
        self.store.set_registered_model_tag(prefix + "RM1", RegisteredModelTag("owner", "aaa"))
        self.store.set_registered_model_tag(prefix + "RM2", RegisteredModelTag("owner", "bbb"))
        self.store.set_registered_model_tag(prefix + "RM3", RegisteredModelTag("owner", "aaa"))
        self.store.set_registered_model_tag(prefix + "RM4", RegisteredModelTag("owner", "ccc"))

    def test_search_registered_models_tags(self):
        prefix = "test_for_search_tags"
        self._set_up_model_and_tags_for_search(prefix)

        result_rms, _ = self._search_registered_models("tags.`training algorithm` = 'lightgbm'")
        self.assertEqual(result_rms, [prefix + name for name in ["RM1", "RM2", "RM3", "RM4"]])

        # test model_tag, tags aliases with like, != operators
        result_rms, _ = self._search_registered_models(
            "model_tag.`training algorithm` like '%gbm' and tags.owner != 'aaa'"
        )
        self.assertEqual(result_rms, [prefix + "RM2", prefix + "RM4"])

        # test tag, registered_model_tag aliases with ilike, != operators
        result_rms, _ = self._search_registered_models(
            "tag.`training algorithm` ilike 'LIGHT%' and registered_model_tag.owner != 'aaa'"
        )
        self.assertEqual(result_rms, [prefix + "RM2", prefix + "RM4"])

        # test registered_model_tags, model_tags aliases with = operator
        result_rms, _ = self._search_registered_models(
            "registered_model_tags.`training algorithm` = 'lightgbm' and model_tags.owner = 'ddd'"
        )
        self.assertEqual(result_rms, [])

        for bad_filter in [
            "tags.training algorithm = 'lightgbm'",
            "tags.owner = kkk",
            "version_tag.owner = 'aaa'",
            "tags.`training algorithm` = 'xgboost' or tags.owner = 'aaa'",
        ]:
            with self.assertRaises(MlflowException) as exception_context:
                self._search_registered_models(bad_filter)
            assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    def test_search_registered_model_complex(self):
        prefix = "test_for_search_model_complex_"
        self._set_up_model_and_tags_for_search(prefix)

        result_rms, _ = self._search_registered_models(
            "tags.`training algorithm` = 'lightgbm' and name like '%RM1'"
        )
        self.assertEqual(result_rms, [prefix + "RM1"])

        result_rms, _ = self._search_registered_models(
            "model_tag.`training algorithm` "
            "like '%boost' and tags.owner != 'aaa'"
            " and attribute.name != '{}RM4'".format(prefix)
        )
        self.assertEqual(result_rms, [])

        result_rms, _ = self._search_registered_models(
            "tag.`training algorithm` ilike 'LIGHT%' "
            "and tags.owner != 'aaa'"
            " and attr.name ilike '%%'"
        )
        self.assertEqual(result_rms, [prefix + "RM2", prefix + "RM4"])

        result_rms, _ = self._search_registered_models(
            "registered_model_tags.`training algorithm` = 'lightgbm' and name = 'jkjk'"
        )
        self.assertEqual(result_rms, [])

        for bad_filter in [
            "tags.`training algorithm` = 'lightgbm' and name IN ['aaa', 'bbb']",
            "tags.owner = kkk and attribute.name = 'RM1'",
            "tag.owner = 'aaa' and attri.name = 'RM2'",
            "tags.`training algorithm` = 'xgboost' or name = 'aaa'",
        ]:
            with self.assertRaises(MlflowException) as exception_context:
                self._search_registered_models(bad_filter)
            assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    def test_get_order_by_clauses_for_registered_models(self):
        with self.store.ManagedSessionMaker() as session:
            # test that "registered_models.name ASC" is returned by default
            parsed = [
                str(x)
                for x in SearchModelsUtils.get_order_by_clauses_for_registered_model([], session)[0]
            ]
            assert parsed == ["registered_models.name ASC"]

            # test that the given 'name' replaces the default one ('registered_models.name ASC')
            parsed = [
                str(x)
                for x in SearchModelsUtils.get_order_by_clauses_for_registered_model(
                    ["registered_models.name DESC"], session
                )[0]
            ]
            assert "registered_models.name DESC" in parsed
            assert "registered_models.name ASC" not in parsed

            # test that an exception is raised when order_by contains duplicate fields
            msg = "`order_by` contains duplicate fields:"
            with self.assertRaisesRegex(MlflowException, msg):
                SearchModelsUtils.get_order_by_clauses_for_registered_model(
                    ["attribute.last_updated_timestamp", "last_updated_timestamp"], session
                )

            with self.assertRaisesRegex(MlflowException, msg):
                SearchModelsUtils.get_order_by_clauses_for_registered_model(
                    ["timestamp", "timestamp"], session
                )

            with self.assertRaisesRegex(MlflowException, msg):
                SearchModelsUtils.get_order_by_clauses_for_registered_model(
                    ["timestamp", "last_updated_timestamp"], session
                )

            with self.assertRaisesRegex(MlflowException, msg):
                SearchModelsUtils.get_order_by_clauses_for_registered_model(
                    ["last_updated_timestamp ASC", "attr.last_updated_timestamp DESC"], session
                )

            with self.assertRaisesRegex(MlflowException, msg):
                SearchModelsUtils.get_order_by_clauses_for_registered_model(
                    ["last_updated_timestamp", "last_updated_timestamp DESC"], session
                )

            with self.assertRaisesRegex(MlflowException, msg):
                SearchModelsUtils.get_order_by_clauses_for_registered_model(
                    ["tags.owner", "tags.owner"], session
                )

            with self.assertRaisesRegex(MlflowException, msg):
                SearchModelsUtils.get_order_by_clauses_for_registered_model(
                    ["tags.`parent model` desc", "tags.`parent model` ASC"], session
                )

    def test_search_registered_model_pagination(self):
        rms = [self._rm_maker("RM{:03}".format(i)).name for i in range(50)]
        for rm in rms:
            self.store.set_registered_model_tag(rm, RegisteredModelTag("passed", "true"))

        # test flow with fixed max_results
        returned_rms = []
        query = "name LIKE 'RM%' and tags.passed = 'true'"
        result, token = self._search_registered_models(query, page_token=None, max_results=5)
        returned_rms.extend(result)
        while token:
            result, token = self._search_registered_models(query, page_token=token, max_results=5)
            returned_rms.extend(result)
        self.assertEqual(rms, returned_rms)

        # test that pagination will return all valid results in sorted order
        # by name ascending
        result, token1 = self._search_registered_models(query, max_results=5)
        self.assertNotEqual(token1, None)
        self.assertEqual(result, rms[0:5])

        result, token2 = self._search_registered_models(query, page_token=token1, max_results=10)
        self.assertNotEqual(token2, None)
        self.assertEqual(result, rms[5:15])

        result, token3 = self._search_registered_models(query, page_token=token2, max_results=20)
        self.assertNotEqual(token3, None)
        self.assertEqual(result, rms[15:35])

        result, token4 = self._search_registered_models(query, page_token=token3, max_results=100)
        # assert that page token is None
        self.assertEqual(token4, None)
        self.assertEqual(result, rms[35:])

        # test that providing a completely invalid page token throws
        with self.assertRaises(MlflowException) as exception_context:
            self._search_registered_models(query, page_token="evilhax", max_results=20)
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

        # test that providing too large of a max_results throws
        with self.assertRaises(MlflowException) as exception_context:
            self._search_registered_models(query, page_token="evilhax", max_results=1e15)
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
        self.assertIn(
            "Invalid value for request parameter max_results", exception_context.exception.message,
        )

    def test_search_registered_model_attribute_order_by(self):
        rms = []
        # explicitly mock the creation_timestamps because timestamps seem to be unstable in Windows
        for i in range(50):
            with mock.patch("mlflow.store.model_registry.sqlalchemy_store.now", return_value=i):
                rms.append(self._rm_maker("RM{:03}".format(i)).name)

        # test flow with fixed max_results and order_by (test stable order across pages)
        returned_rms = []
        query = "name LIKE 'RM%'"
        result, token = self._search_registered_models(
            query, page_token=None, order_by=["name DESC"], max_results=5
        )
        returned_rms.extend(result)
        while token:
            result, token = self._search_registered_models(
                query, page_token=token, order_by=["name DESC"], max_results=5
            )
            returned_rms.extend(result)
        # name descending should be the opposite order of the current order
        self.assertEqual(rms[::-1], returned_rms)
        # last_updated_timestamp descending should have the newest RMs first
        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["last_updated_timestamp DESC"], max_results=100,
        )
        self.assertEqual(rms[::-1], result)
        # timestamp returns same result as last_updated_timestamp
        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["timestamp DESC"], max_results=100
        )
        self.assertEqual(rms[::-1], result)
        # last_updated_timestamp ascending should have the oldest RMs first
        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["last_updated_timestamp ASC"], max_results=100,
        )
        self.assertEqual(rms, result)
        # timestamp returns same result as last_updated_timestamp
        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["timestamp ASC"], max_results=100
        )
        self.assertEqual(rms, result)
        # timestamp returns same result as last_updated_timestamp
        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["timestamp"], max_results=100
        )
        self.assertEqual(rms, result)
        # name ascending should have the original order
        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["name ASC"], max_results=100
        )
        self.assertEqual(rms, result)
        # test that no ASC/DESC defaults to ASC
        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["last_updated_timestamp"], max_results=100
        )
        self.assertEqual(rms, result)
        with mock.patch("mlflow.store.model_registry.sqlalchemy_store.now", return_value=1):
            rm1 = self._rm_maker("MR1").name
            rm2 = self._rm_maker("MR2").name
        with mock.patch("mlflow.store.model_registry.sqlalchemy_store.now", return_value=2):
            rm3 = self._rm_maker("MR3").name
            rm4 = self._rm_maker("MR4").name
        query = "name LIKE 'MR%'"
        # test with multiple clauses
        result, _ = self._search_registered_models(
            query,
            page_token=None,
            order_by=["last_updated_timestamp ASC", "name DESC"],
            max_results=100,
        )
        self.assertEqual([rm2, rm1, rm4, rm3], result)
        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["timestamp ASC", "name   DESC"], max_results=100,
        )
        self.assertEqual([rm2, rm1, rm4, rm3], result)
        # confirm that name ascending is the default, even if ties exist on other fields
        result, _ = self._search_registered_models(
            query, page_token=None, order_by=[], max_results=100
        )
        self.assertEqual([rm1, rm2, rm3, rm4], result)
        # test default tiebreak with descending timestamps
        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["last_updated_timestamp DESC"], max_results=100,
        )
        self.assertEqual([rm3, rm4, rm1, rm2], result)
        # test timestamp parsing
        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["timestamp\tASC"], max_results=100
        )
        self.assertEqual([rm1, rm2, rm3, rm4], result)
        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["timestamp\r\rASC"], max_results=100
        )
        self.assertEqual([rm1, rm2, rm3, rm4], result)
        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["timestamp\nASC"], max_results=100
        )
        self.assertEqual([rm1, rm2, rm3, rm4], result)
        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["timestamp  ASC"], max_results=100
        )
        self.assertEqual([rm1, rm2, rm3, rm4], result)
        # validate order by key is case-insensitive
        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["timestamp  asc"], max_results=100
        )
        self.assertEqual([rm1, rm2, rm3, rm4], result)
        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["timestamp  aSC"], max_results=100
        )
        self.assertEqual([rm1, rm2, rm3, rm4], result)
        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["timestamp  desc", "name desc"], max_results=100,
        )
        self.assertEqual([rm4, rm3, rm2, rm1], result)
        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["timestamp  deSc", "name deSc"], max_results=100,
        )
        self.assertEqual([rm4, rm3, rm2, rm1], result)

    def test_search_registered_model_tags_order_by(self):
        rms = []
        start_char = "A"
        for i in range(50):
            name = self._rm_maker("RM{:03}".format(i)).name
            rms.append(name)
            # use incrementing ascii char as tag value to make sure ordering is correct
            self.store.set_registered_model_tag(
                name, RegisteredModelTag("order id", chr(ord(start_char) + i))
            )

        # test flow with fixed max_results and order_by (test stable order across pages)
        returned_rms = []
        query = "name LIKE 'RM%'"
        result, token = self._search_registered_models(
            query, page_token=None, order_by=["tags.`order id` DESC"], max_results=5
        )
        returned_rms.extend(result)
        while token:
            result, token = self._search_registered_models(
                query, page_token=token, order_by=["tags.`order id` DESC"], max_results=5,
            )
            returned_rms.extend(result)
        # name descending should be the opposite order of the current order
        self.assertEqual(rms[::-1], returned_rms)

        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["tags.`order id`"], max_results=100
        )
        self.assertEqual(rms, result)

        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["tags.`order id` asc"], max_results=100
        )
        self.assertEqual(rms, result)

        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["tags.`order id` DESC"], max_results=100
        )
        self.assertEqual(rms[::-1], result)

        with mock.patch("mlflow.store.model_registry.sqlalchemy_store.now", return_value=1):
            rm1 = self._rm_maker("MR1").name
            self.store.set_registered_model_tag(rm1, RegisteredModelTag("number", "1"))
            rm2 = self._rm_maker("MR2").name
            self.store.set_registered_model_tag(rm2, RegisteredModelTag("number", "2"))
        with mock.patch("mlflow.store.model_registry.sqlalchemy_store.now", return_value=2):
            rm3 = self._rm_maker("MR3").name
            self.store.set_registered_model_tag(rm3, RegisteredModelTag("number", "3"))
            rm4 = self._rm_maker("MR4").name
            self.store.set_registered_model_tag(rm4, RegisteredModelTag("number", "4"))

        query = "name LIKE 'MR%'"
        # test with multiple clauses
        result, _ = self._search_registered_models(
            query,
            page_token=None,
            order_by=["last_updated_timestamp ASC", "tag.number DESC"],
            max_results=100,
        )
        self.assertEqual([rm2, rm1, rm4, rm3], result)
        result, _ = self._search_registered_models(
            query, page_token=None, order_by=["timestamp ASC", "tag.number  DESC"], max_results=100,
        )
        self.assertEqual([rm2, rm1, rm4, rm3], result)

    def test_search_registered_model_order_by_errors(self):
        query = "name LIKE 'RM%'"
        # test that invalid columns throw even if they come after valid columns
        with self.assertRaises(MlflowException) as exception_context:
            self._search_registered_models(
                query,
                page_token=None,
                order_by=["name ACS kk", "creation_timestamp DESC"],
                max_results=5,
            )
        print(exception_context.exception.message)
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
        # test that invalid columns with random text throw even if they come after valid columns
        with self.assertRaises(MlflowException) as exception_context:
            self._search_registered_models(
                query,
                page_token=None,
                order_by=["name Acs", "last_updated_timestamp DESC blah"],
                max_results=5,
            )
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    def test_set_model_version_tag(self):
        name1 = "SetModelVersionTag_TestMod"
        name2 = "SetModelVersionTag_TestMod 2"
        initial_tags = [
            ModelVersionTag("key", "value"),
            ModelVersionTag("anotherKey", "some other value"),
        ]
        self._rm_maker(name1)
        self._rm_maker(name2)
        run_id_1 = uuid.uuid4().hex
        run_id_2 = uuid.uuid4().hex
        run_id_3 = uuid.uuid4().hex
        self._mv_maker(name1, "A/B", run_id_1, initial_tags)
        self._mv_maker(name1, "A/C", run_id_2, initial_tags)
        self._mv_maker(name2, "A/D", run_id_3, initial_tags)
        new_tag = ModelVersionTag("randomTag", "not a random value")
        self.store.set_model_version_tag(name1, 1, new_tag)
        all_tags = initial_tags + [new_tag]
        rm1mv1 = self.store.get_model_version(name1, 1)
        self.assertEqual(rm1mv1.tags, {tag.key: tag.value for tag in all_tags})

        # test overriding a tag with the same key
        overriding_tag = ModelVersionTag("key", "overriding")
        self.store.set_model_version_tag(name1, 1, overriding_tag)
        all_tags = [tag for tag in all_tags if tag.key != "key"] + [overriding_tag]
        rm1mv1 = self.store.get_model_version(name1, 1)
        self.assertEqual(rm1mv1.tags, {tag.key: tag.value for tag in all_tags})
        # does not affect other model versions with the same key
        rm1mv2 = self.store.get_model_version(name1, 2)
        rm2mv1 = self.store.get_model_version(name2, 1)
        self.assertEqual(rm1mv2.tags, {tag.key: tag.value for tag in initial_tags})
        self.assertEqual(rm2mv1.tags, {tag.key: tag.value for tag in initial_tags})

        # can not set tag on deleted (non-existed) model version
        self.store.delete_model_version(name1, 2)
        with self.assertRaises(MlflowException) as exception_context:
            self.store.set_model_version_tag(name1, 2, overriding_tag)
        assert exception_context.exception.error_code == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST)
        # test cannot set tags that are too long
        long_tag = ModelVersionTag("longTagKey", "a" * 5001)
        with self.assertRaises(MlflowException) as exception_context:
            self.store.set_model_version_tag(name1, 1, long_tag)
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
        # test can set tags that are somewhat long
        long_tag = ModelVersionTag("longTagKey", "a" * 4999)
        self.store.set_model_version_tag(name1, 1, long_tag)
        # can not set invalid tag
        with self.assertRaises(MlflowException) as exception_context:
            self.store.set_model_version_tag(name2, 1, ModelVersionTag(key=None, value=""))
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
        # can not use invalid model name or version
        with self.assertRaises(MlflowException) as exception_context:
            self.store.set_model_version_tag(None, 1, ModelVersionTag(key="key", value="value"))
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
        with self.assertRaises(MlflowException) as exception_context:
            self.store.set_model_version_tag(
                name2, "I am not a version", ModelVersionTag(key="key", value="value")
            )
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)

    def test_delete_model_version_tag(self):
        name1 = "DeleteModelVersionTag_TestMod"
        name2 = "DeleteModelVersionTag_TestMod 2"
        initial_tags = [
            ModelVersionTag("key", "value"),
            ModelVersionTag("anotherKey", "some other value"),
        ]
        self._rm_maker(name1)
        self._rm_maker(name2)
        run_id_1 = uuid.uuid4().hex
        run_id_2 = uuid.uuid4().hex
        run_id_3 = uuid.uuid4().hex
        self._mv_maker(name1, "A/B", run_id_1, initial_tags)
        self._mv_maker(name1, "A/C", run_id_2, initial_tags)
        self._mv_maker(name2, "A/D", run_id_3, initial_tags)
        new_tag = ModelVersionTag("randomTag", "not a random value")
        self.store.set_model_version_tag(name1, 1, new_tag)
        self.store.delete_model_version_tag(name1, 1, "randomTag")
        rm1mv1 = self.store.get_model_version(name1, 1)
        self.assertEqual(rm1mv1.tags, {tag.key: tag.value for tag in initial_tags})

        # testing deleting a key does not affect other model versions with the same key
        self.store.delete_model_version_tag(name1, 1, "key")
        rm1mv1 = self.store.get_model_version(name1, 1)
        rm1mv2 = self.store.get_model_version(name1, 2)
        rm2mv1 = self.store.get_model_version(name2, 1)
        self.assertEqual(rm1mv1.tags, {"anotherKey": "some other value"})
        self.assertEqual(rm1mv2.tags, {tag.key: tag.value for tag in initial_tags})
        self.assertEqual(rm2mv1.tags, {tag.key: tag.value for tag in initial_tags})

        # delete tag that is already deleted does nothing
        self.store.delete_model_version_tag(name1, 1, "key")
        rm1mv1 = self.store.get_model_version(name1, 1)
        self.assertEqual(rm1mv1.tags, {"anotherKey": "some other value"})

        # can not delete tag on deleted (non-existed) model version
        self.store.delete_model_version(name2, 1)
        with self.assertRaises(MlflowException) as exception_context:
            self.store.delete_model_version_tag(name2, 1, "key")
        assert exception_context.exception.error_code == ErrorCode.Name(RESOURCE_DOES_NOT_EXIST)
        # can not delete tag with invalid key
        with self.assertRaises(MlflowException) as exception_context:
            self.store.delete_model_version_tag(name1, 2, None)
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
        # can not use invalid model name or version
        with self.assertRaises(MlflowException) as exception_context:
            self.store.delete_model_version_tag(None, 2, "key")
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
        with self.assertRaises(MlflowException) as exception_context:
            self.store.delete_model_version_tag(name1, "I am not a version", "key")
        assert exception_context.exception.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)
