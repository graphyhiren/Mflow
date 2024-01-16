import math

import json
import keras
import pandas as pd
import numpy as np
import pytest
from mlflow.types import Schema, TensorSpec
from mlflow.models.model import MLMODEL_FILE_NAME
from mlflow.tracking.fluent import flush_async_logging

import mlflow
from mlflow.keras.utils import get_model_signature
from mlflow import MlflowClient
import yaml
import os
from mlflow.utils.autologging_utils import AUTOLOGGING_INTEGRATIONS


@pytest.fixture(autouse=True)
def clear_autologging_config():
    yield
    AUTOLOGGING_INTEGRATIONS.pop("keras", None)


def _create_keras_model():
    model = keras.Sequential(
        [
            keras.Input([28, 28, 3]),
            keras.layers.Flatten(),
            keras.layers.Dense(2),
        ]
    )

    model.compile(
        loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        optimizer=keras.optimizers.Adam(0.001),
        metrics=[keras.metrics.SparseCategoricalAccuracy()],
    )
    return model


def _check_logged_model_signature_is_expected(run, input_schema, output_schema):
    artifacts_dir = run.info.artifact_uri.replace("file://", "")
    client = MlflowClient()
    artifacts = [x.path for x in client.list_artifacts(run.info.run_id, "model")]
    ml_model_filename = "MLmodel"
    assert str(os.path.join("model", ml_model_filename)) in artifacts
    ml_model_path = os.path.join(artifacts_dir, "model", ml_model_filename)
    with open(ml_model_path) as f:
        model_config = yaml.load(f, Loader=yaml.FullLoader)
        assert model_config is not None
        assert "signature" in model_config
        signature = model_config["signature"]
        assert signature is not None
        assert "inputs" in signature
        assert "outputs" in signature
        assert signature["inputs"] == input_schema.to_json()
        assert signature["outputs"] == output_schema.to_json()


def test_default_autolog_behavior():
    mlflow.keras.autolog()

    # Prepare data for a 2-class classification.
    data = np.random.uniform(size=(20, 28, 28, 3))
    label = np.random.randint(2, size=20)

    model = _create_keras_model()

    num_epochs = 2
    batch_size = 4
    with mlflow.start_run() as run:
        model.fit(
            data,
            label,
            validation_data=(data, label),
            batch_size=batch_size,
            epochs=num_epochs,
        )
    flush_async_logging()
    client = mlflow.MlflowClient()
    mlflow_run = client.get_run(run.info.run_id)
    run_metrics = mlflow_run.data.metrics
    model_info = mlflow_run.data.params

    # Assert training configs are logged correctly.
    assert int(model_info["batch_size"]) == batch_size
    assert model_info["optimizer_name"] == "adam"
    assert math.isclose(float(model_info["optimizer_learning_rate"]), 0.001, rel_tol=1e-6)

    assert "loss" in run_metrics
    assert "sparse_categorical_accuracy" in run_metrics
    assert "validation_loss" in run_metrics

    # Assert metrics are logged in the correct number of times.
    loss_history = client.get_metric_history(run_id=run.info.run_id, key="loss")
    assert len(loss_history) == num_epochs

    validation_loss_history = client.get_metric_history(
        run_id=run.info.run_id,
        key="validation_loss",
    )
    assert len(validation_loss_history) == num_epochs

    # Test the loaded pyfunc model produces the same output for the same input as the model.
    test_input = np.random.uniform(size=[2, 28, 28, 3]).astype(np.float32)
    logged_model = f"runs:/{run.info.run_id}/model"
    loaded_pyfunc_model = mlflow.pyfunc.load_model(logged_model)
    np.testing.assert_allclose(
        keras.ops.convert_to_numpy(model(test_input)),
        loaded_pyfunc_model.predict(test_input),
    )

    # Test the signature is logged.
    input_schema = Schema([TensorSpec(np.dtype(np.float32), (-1, 28, 28, 3))])
    output_schema = Schema([TensorSpec(np.dtype(np.float32), (-1, 2))])
    _check_logged_model_signature_is_expected(run, input_schema, output_schema)


def test_custom_autolog_behavior():
    mlflow.keras.autolog(
        log_every_epoch=False,
        log_every_n_steps=1,
        log_models=False,
        log_datasets=False,
        log_model_signatures=False,
    )

    # Prepare data for a 2-class classification.
    data = np.random.uniform(size=(20, 28, 28, 3))
    label = np.random.randint(2, size=20)

    model = _create_keras_model()

    num_epochs = 1
    batch_size = 4
    with mlflow.start_run() as run:
        model.fit(
            data,
            label,
            validation_data=(data, label),
            batch_size=batch_size,
            epochs=num_epochs,
        )
    flush_async_logging()
    client = mlflow.MlflowClient()
    mlflow_run = client.get_run(run.info.run_id)
    run_metrics = mlflow_run.data.metrics
    model_info = mlflow_run.data.params

    # Assert training configs are logged correctly.
    assert int(model_info["batch_size"]) == batch_size
    assert model_info["optimizer_name"] == "adam"
    assert math.isclose(float(model_info["optimizer_learning_rate"]), 0.001, rel_tol=1e-6)

    assert "loss" in run_metrics
    assert "sparse_categorical_accuracy" in run_metrics
    assert "validation_loss" in run_metrics

    # Assert metrics are logged in the correct number of times.
    loss_history = client.get_metric_history(run_id=run.info.run_id, key="loss")
    assert len(loss_history) == num_epochs * (data.shape[0] // batch_size)

    validation_loss_history = client.get_metric_history(
        run_id=run.info.run_id,
        key="validation_loss",
    )
    assert len(validation_loss_history) == num_epochs

    # Test the model is not logged.
    assert "mlflow.log-model.history" not in mlflow_run.data.tags


@pytest.mark.parametrize("log_datasets", [True, False])
def test_keras_autolog_log_datasets(log_datasets):
    mlflow.keras.autolog(log_datasets=log_datasets)

    # Prepare data for a 2-class classification.
    data = np.random.uniform(size=(20, 28, 28, 3)).astype(np.float32)
    label = np.random.randint(2, size=20)

    model = _create_keras_model()

    model.fit(data, label, epochs=2)
    flush_async_logging()
    client = mlflow.MlflowClient()
    dataset_inputs = client.get_run(mlflow.last_active_run().info.run_id).inputs.dataset_inputs
    if log_datasets:
        assert len(dataset_inputs) == 1
        feature_schema = Schema(
            [
                TensorSpec(np.dtype(np.float32), (-1, 28, 28, 3)),
            ]
        )
        target_schema = Schema(
            [
                TensorSpec(np.dtype(np.int64), (-1,)),
            ]
        )
        expected = json.dumps(
            {
                "mlflow_tensorspec": {
                    "features": feature_schema.to_json(),
                    "targets": target_schema.to_json(),
                }
            }
        )
        assert dataset_inputs[0].dataset.schema == expected
    else:
        assert len(dataset_inputs) == 0
