import json
import math
import numpy as np
import pandas as pd
import pytest

from mlflow.models.signature import infer_signature
from mlflow.models.utils import _Example, _read_tensor_input_from_json
from mlflow.types.utils import TensorsNotSupportedException
from mlflow.utils.file_utils import TempDir
from mlflow.utils.proto_json_utils import _dataframe_from_json


@pytest.fixture
def pandas_df_with_all_types():
    return pd.DataFrame(
        {
            "boolean": [True, False, True],
            "integer": np.array([1, 2, 3], np.int32),
            "long": np.array([1, 2, 3], np.int64),
            "float": np.array([math.pi, 2 * math.pi, 3 * math.pi], np.float32),
            "double": [math.pi, 2 * math.pi, 3 * math.pi],
            "binary": [bytes([1, 2, 3]), bytes([4, 5, 6]), bytes([7, 8, 9])],
            "string": ["a", "b", "c"],
        }
    )


@pytest.fixture
def dict_of_ndarrays():
    return {
        "1D": np.arange(0, 12, 0.5),
        "2D": np.arange(0, 12, 0.5).reshape(3, 8),
        "3D": np.arange(0, 12, 0.5).reshape(2, 3, 4),
        "4D": np.arange(0, 12, 0.5).reshape(3, 2, 2, 2),
    }


def test_input_examples(pandas_df_with_all_types, dict_of_ndarrays):
    sig = infer_signature(pandas_df_with_all_types)
    # test setting example with data frame with all supported data types
    with TempDir() as tmp:
        example = _Example(pandas_df_with_all_types)
        example.save(tmp.path())
        filename = example.info["artifact_path"]
        with open(tmp.path(filename), "r") as f:
            data = json.load(f)
            assert set(data.keys()) == set(("columns", "data"))
        parsed_df = _dataframe_from_json(tmp.path(filename), schema=sig.inputs)
        assert (pandas_df_with_all_types == parsed_df).all().all()
        # the frame read without schema should match except for the binary values
        assert (
            (
                parsed_df.drop(columns=["binary"])
                == _dataframe_from_json(tmp.path(filename)).drop(columns=["binary"])
            )
            .all()
            .all()
        )

    # pass the input as dictionary instead
    with TempDir() as tmp:
        d = {
            name: pandas_df_with_all_types[name].values for name in pandas_df_with_all_types.columns
        }
        example = _Example(d)
        example.save(tmp.path())
        filename = example.info["artifact_path"]
        parsed_df = _dataframe_from_json(tmp.path(filename), sig.inputs)
        assert (pandas_df_with_all_types == parsed_df).all().all()

    # input passed as numpy array
    # NB: Drop columns whose values cannot be encoded using proto_json_utils.pyNumpyEncoder
    new_df = pandas_df_with_all_types.drop(columns=["boolean", "binary", "string"])
    for col in new_df:
        input_example = new_df[col].to_numpy()
        with TempDir() as tmp:
            example = _Example(input_example)
            example.save(tmp.path())
            filename = example.info["artifact_path"]
            with open(tmp.path(filename), "r") as f:
                data = json.load(f)
                assert set(data.keys()) == set(("instances",))
            parsed_ary = _read_tensor_input_from_json(tmp.path(filename))
            assert np.array_equal(parsed_ary, input_example)

    # pass multidimensional array
    for col in dict_of_ndarrays:
        input_example = dict_of_ndarrays[col]
        with TempDir() as tmp:
            example = _Example(input_example)
            example.save(tmp.path())
            filename = example.info["artifact_path"]
            with open(tmp.path(filename), "r") as f:
                data = json.load(f)
                assert set(data.keys()) == set(("instances",))
            parsed_ary = _read_tensor_input_from_json(tmp.path(filename))
            assert np.array_equal(parsed_ary, input_example)

    # pass multidimensional array as a dictionary or list
    with TempDir() as tmp:
        example = np.array([[1, 2, 3]])
        with pytest.raises(TensorsNotSupportedException):
            _Example({"x": example, "y": example})
        with pytest.raises(TensorsNotSupportedException):
            _Example([example, example])

    # pass dict with scalars
    with TempDir() as tmp:
        example = {"a": 1, "b": "abc"}
        x = _Example(example)
        x.save(tmp.path())
        filename = x.info["artifact_path"]
        parsed_df = _dataframe_from_json(tmp.path(filename))
        assert example == parsed_df.to_dict(orient="records")[0]
