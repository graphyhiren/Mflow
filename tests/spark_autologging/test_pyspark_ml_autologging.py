import importlib
import inspect
import pytest
from collections import namedtuple
from unittest import mock

import mlflow
from mlflow.utils import (
    truncate_dict,
)
from mlflow.utils.validation import (
    MAX_PARAM_VAL_LENGTH,
    MAX_ENTITY_KEY_LENGTH,
)

from tests.autologging.fixtures import test_mode_off
from tests.spark_autologging.utils import spark_session  # pylint: disable=unused-import
from pyspark.ml.linalg import Vectors
from pyspark.ml.regression import LinearRegression
from mlflow.pyspark.ml import _should_log_model, _get_instance_param_map, _log_model_allowlist

MODEL_DIR = "model"
MLFLOW_PARENT_RUN_ID = "mlflow.parentRunId"


@pytest.fixture(scope="module")
def dataset_binary(spark_session):
    yield spark_session.createDataFrame(
        [(1.0, Vectors.dense(1.0)),
         (0.0, Vectors.sparse(1, [], []))] * 100,
        ["label", "features"])


@pytest.fixture(scope="module")
def dataset_20_classes(spark_session):
    label_list = list(range(20)) * 10
    features_list = [Vectors.dense(1.0),
                     Vectors.sparse(1, [], [])] * 100
    yield spark_session.createDataFrame(
        zip(label_list, features_list),
        ["label", "features"])


def truncate_param_dict(d):
    return truncate_dict(d, MAX_ENTITY_KEY_LENGTH, MAX_PARAM_VAL_LENGTH)


def stringify_dict_values(d):
    return {k: str(v) for k, v in d.items()}


def get_expected_class_tags(estimator):
    return {
        'estimator_name': estimator.__class__.__name__,
        'estimator_class': estimator.__class__.__module__ + "." + estimator.__class__.__name__,
    }


def get_run_data(run_id):
    client = mlflow.tracking.MlflowClient()
    data = client.get_run(run_id).data
    # Ignore tags mlflow logs by default (e.g. "mlflow.user")
    tags = {k: v for k, v in data.tags.items() if not k.startswith("mlflow.")}
    artifacts = [f.path for f in client.list_artifacts(run_id)]

    RunData = namedtuple('RunData', ['params', 'metrics', 'tags', 'artifacts'])
    return RunData(data.params, data.metrics, tags, artifacts)


def load_model_by_run_id(run_id):
    return mlflow.spark.load_model("runs:/{}/{}".format(run_id, MODEL_DIR))


def get_dataset_binary(spark_session):
    return spark_session.createDataFrame(
        [(1.0, Vectors.dense(1.0)),
         (0.0, Vectors.sparse(1, [], []))] * 100,
        ["label", "features"])


def test_basic_estimator(dataset_binary):
    mlflow.pyspark.ml.autolog()
    lr = LinearRegression()
    with mlflow.start_run() as run:
        lr_model = lr.fit(dataset_binary)
    run_id = run.info.run_id
    run_data = get_run_data(run_id)
    assert run_data.params == \
           truncate_param_dict(stringify_dict_values(_get_instance_param_map(lr)))
    assert run_data.tags == get_expected_class_tags(lr)
    assert MODEL_DIR in run_data.artifacts
    loaded_model = load_model_by_run_id(run_id)
    assert loaded_model.stages[0].uid == lr_model.uid


def test_allowlist_file():
    def estimator_does_not_exist(estimator_class):
        module_name, class_name = estimator_class.rsplit('.', 1)
        try:
            module = importlib.import_module(module_name)
            return not hasattr(module, class_name)
        except ModuleNotFoundError:
            return True

    classes_does_not_exist = list(filter(estimator_does_not_exist, _log_model_allowlist))
    assert len(classes_does_not_exist) == 0, \
        "{} in log_model_allowlist don't exist".format(classes_does_not_exist)


def test_autolog_preserves_original_function_attributes():
    from pyspark.ml import Estimator

    def get_func_attrs(f):
        attrs = {}
        for attr_name in ["__doc__", "__name__"]:
            if hasattr(f, attr_name):
                attrs[attr_name] = getattr(f, attr_name)

        attrs["__signature__"] = inspect.signature(f)
        return attrs

    before = get_func_attrs(getattr(Estimator, 'fit'))
    mlflow.pyspark.ml.autolog()
    after = get_func_attrs(getattr(Estimator, 'fit'))

    for b, a in zip(before, after):
        assert b == a


def test_autolog_does_not_terminate_active_run(dataset_binary):
    mlflow.pyspark.ml.autolog()
    mlflow.start_run()
    lr = LinearRegression()
    lr.fit(dataset_binary)
    assert mlflow.active_run() is not None
    mlflow.end_run()


def test_meta_estimator_fit_performs_logging_only_once(dataset_binary):
    from pyspark.ml.classification import LogisticRegression, OneVsRest
    mlflow.pyspark.ml.autolog()
    with mock.patch("mlflow.log_params") as mock_log_params, \
            mock.patch("mlflow.set_tags") as mock_set_tags, \
            mock.patch("mlflow.spark.log_model") as mock_log_model:
        with mlflow.start_run() as run:
            lor = LogisticRegression()
            ova = OneVsRest(classifier=lor)
            ova.fit(dataset_binary)

        mock_log_params.assert_called_once()
        mock_set_tags.assert_called_once()
        mock_log_model.assert_called_once()

        query = "tags.{} = '{}'".format(MLFLOW_PARENT_RUN_ID, run.info.run_id)
        assert len(mlflow.search_runs([run.info.experiment_id])) == 1
        assert len(mlflow.search_runs([run.info.experiment_id], query)) == 0


def test_fit_with_params(dataset_binary):
    mlflow.pyspark.ml.autolog()
    lr = LinearRegression()
    extra_params = {lr.maxIter: 3, lr.standardization: False}
    extra_params2 = {lr.maxIter: 4, lr.standardization: True}
    # Test calling fit with extra params
    with mlflow.start_run() as run:
        lr.fit(dataset_binary, params=extra_params)
    run_id = run.info.run_id
    run_data = get_run_data(run_id)
    assert run_data.params == truncate_param_dict(stringify_dict_values(
        _get_instance_param_map(lr.copy(extra_params))))

    # Test calling fit with a list/tuple of paramMap
    with mock.patch("mlflow.log_params") as mock_log_params, \
            mock.patch("mlflow.set_tags") as mock_set_tags, \
            mock.patch("mlflow.spark.log_model") as mock_log_model:

        with mlflow.start_run() as run:
            lr.fit(dataset_binary, params=[extra_params, extra_params2])
            lr.fit(dataset_binary, params=(extra_params, extra_params2))

        mock_log_params.assert_not_called()
        mock_set_tags.assert_not_called()
        mock_log_model.assert_not_called()


def test_should_log_model(dataset_binary, dataset_20_classes):
    from pyspark.ml.classification import LogisticRegression, OneVsRest
    lor = LogisticRegression()

    ova1 = OneVsRest(classifier=lor)
    ova_bin_model = ova1.fit(dataset_20_classes)
    assert not _should_log_model(ova1, ova_bin_model)

    blor_model = lor.fit(dataset_binary)
    assert _should_log_model(lor, blor_model)

    mlor20_model = lor.fit(dataset_20_classes)
    assert not _should_log_model(lor, mlor20_model)

    with mock.patch("mlflow.pyspark.ml._log_model_allowlist",
                    'pyspark.ml.regression.LinearRegression\n'):
        lr = LinearRegression()
        lr_model = lr.fit(dataset_binary)
        assert _should_log_model(lr, lr_model)
        assert not _should_log_model(lor, blor_model)


def test_internal_params(spark_session):
    from pyspark.ml.classification import LogisticRegression, OneVsRest
    lor = LogisticRegression(maxIter=3, standardization=False)
    ova = OneVsRest(classifier=lor, labelCol='abcd')

    param_map = _get_instance_param_map(ova)
    assert param_map['labelCol'] == 'abcd'
    assert param_map['classifier'] == lor.uid
    assert param_map[f'{lor.uid}.maxIter'] == 3
    assert param_map[f'{lor.uid}.standardization'] == False
    assert param_map[f'{lor.uid}.tol'] == lor.getOrDefault(lor.tol)

# test warning message

# test_unsupported_versions
