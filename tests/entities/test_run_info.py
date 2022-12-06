import random
import pytest
import uuid

from mlflow.entities import RunInfo, LifecycleStage, RunStatus
from tests.helper_functions import random_str, random_int


def _check(
    ri,
    run_id,
    experiment_id,
    user_id,
    status,
    start_time,
    end_time,
    lifecycle_stage,
    artifact_uri,
):
    assert isinstance(ri, RunInfo)
    assert ri.run_uuid == run_id
    assert ri.run_id == run_id
    assert ri.experiment_id == experiment_id
    assert ri.user_id == user_id
    assert ri.status == status
    assert ri.start_time == start_time
    assert ri.end_time == end_time
    assert ri.lifecycle_stage == lifecycle_stage
    assert ri.artifact_uri == artifact_uri


@pytest.fixture(scope="module")
def run_info_test_params():
    run_id = str(uuid.uuid4())
    experiment_id = str(random_int(10, 2000))
    user_id = random_str(random_int(10, 25))
    run_name = random_str(random_int(10, 25))
    status = RunStatus.to_string(random.choice(RunStatus.all_status()))
    start_time = random_int(1, 10)
    end_time = start_time + random_int(1, 10)
    lifecycle_stage = LifecycleStage.ACTIVE
    artifact_uri = random_str(random_int(10, 40))
    ri = RunInfo(
        run_uuid=run_id,
        run_id=run_id,
        run_name=run_name,
        experiment_id=experiment_id,
        user_id=user_id,
        status=status,
        start_time=start_time,
        end_time=end_time,
        lifecycle_stage=lifecycle_stage,
        artifact_uri=artifact_uri,
    )
    yield (
        ri,
        run_id,
        run_name,
        experiment_id,
        user_id,
        status,
        start_time,
        end_time,
        lifecycle_stage,
        artifact_uri,
    )


def test_creation_and_hydration(run_info_test_params):
    (
        ri1,
        run_id,
        run_name,
        experiment_id,
        user_id,
        status,
        start_time,
        end_time,
        lifecycle_stage,
        artifact_uri,
    ) = run_info_test_params
    _check(
        ri1,
        run_id,
        experiment_id,
        user_id,
        status,
        start_time,
        end_time,
        lifecycle_stage,
        artifact_uri,
    )
    as_dict = {
        "run_uuid": run_id,
        "run_id": run_id,
        "run_name": run_name,
        "experiment_id": experiment_id,
        "user_id": user_id,
        "status": status,
        "start_time": start_time,
        "end_time": end_time,
        "lifecycle_stage": lifecycle_stage,
        "artifact_uri": artifact_uri,
    }
    assert dict(ri1) == as_dict

    proto = ri1.to_proto()
    ri2 = RunInfo.from_proto(proto)
    _check(
        ri2,
        run_id,
        experiment_id,
        user_id,
        status,
        start_time,
        end_time,
        lifecycle_stage,
        artifact_uri,
    )
    ri3 = RunInfo.from_dictionary(as_dict)
    _check(
        ri3,
        run_id,
        experiment_id,
        user_id,
        status,
        start_time,
        end_time,
        lifecycle_stage,
        artifact_uri,
    )
    # Test that we can add a field to RunInfo and still deserialize it from a dictionary
    dict_copy_0 = as_dict.copy()
    dict_copy_0["my_new_field"] = "new field value"
    ri4 = RunInfo.from_dictionary(dict_copy_0)
    _check(
        ri4,
        run_id,
        experiment_id,
        user_id,
        status,
        start_time,
        end_time,
        lifecycle_stage,
        artifact_uri,
    )


def test_searchable_attributes():
    assert set(RunInfo.get_searchable_attributes()) == {
        "status",
        "artifact_uri",
        "start_time",
        "user_id",
        "end_time",
        "run_name",
        "run_id",
    }
