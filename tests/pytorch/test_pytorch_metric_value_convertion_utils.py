import pytest
from unittest import mock

import mlflow
from mlflow import tracking
from mlflow.tracking.fluent import start_run
from mlflow.exceptions import MlflowException, INVALID_PARAMETER_VALUE, ErrorCode
from mlflow.tracking.metric_value_conversion_utils import *

import torch


def test_reraised_value_errors():
    multi_item_torch_tensor = torch.rand((2, 2))

    with pytest.raises(MlflowException) as e:
        convert_metric_value_to_float_if_possible(multi_item_torch_tensor)

    assert e.value.error_code == ErrorCode.Name(INVALID_PARAMETER_VALUE)


def test_convert_metric_value_to_float():
    torch_tensor_val = torch.rand(1)
    assert float(torch_tensor_val[0]) == convert_metric_value_to_float_if_possible(torch_tensor_val)


def test_log_torch_tensor_as_metric():
    torch_tensor_val = torch.rand(1)
    torch_tensor_float_val = float(torch_tensor_val[0])

    with start_run() as run:
        mlflow.log_metric("name_torch", torch_tensor_val)

    finished_run = tracking.MlflowClient().get_run(run.info.run_id)
    expected_pairs = {"name_torch": torch_tensor_float_val}
