import os
from unittest import mock

import pytest
import yaml

from mlflow.models import ModelConfig

dir_path = os.path.dirname(os.path.abspath(__file__))
VALID_CONFIG_PATH = os.path.join(dir_path, "configs/config.yaml")
VALID_CONFIG_PATH_2 = os.path.join(dir_path, "configs/config_2.yaml")


def test_config_not_set():
    with pytest.raises(
        FileNotFoundError, match="Config file is None. Please provide a valid path."
    ):
        ModelConfig()


@mock.patch("mlflow.langchain._rag_utils")
def test_config_not_found(mock_rag_config_path):
    mock_rag_config_path.__databricks_rag_config_path__ = "nonexistent.yaml"
    with pytest.raises(FileNotFoundError, match="Config file 'nonexistent.yaml' not found."):
        ModelConfig(development_config="nonexistent.yaml")


def test_config_invalid_yaml(tmp_path):
    tmp_file = tmp_path / "invalid_config.yaml"
    tmp_file.write_text("invalid_yaml: \n  - this is not valid \n-yaml")
    config = ModelConfig(development_config=str(tmp_file))
    with pytest.raises(yaml.YAMLError, match="Error parsing YAML file: "):
        config.get("key")


def test_config_key_not_found():
    config = ModelConfig(development_config=VALID_CONFIG_PATH)
    with pytest.raises(KeyError, match="Key 'key' not found in configuration: "):
        config.get("key")


def test_config_setup_correctly():
    config = ModelConfig(development_config=VALID_CONFIG_PATH)
    assert config.get("llm_parameters").get("temperature") == 0.01


@mock.patch("mlflow.langchain._rag_utils")
def test_config_setup_correctly_with_mlflow_langchain(mock_rag_config_path):
    mock_rag_config_path.__databricks_rag_config_path__ = VALID_CONFIG_PATH
    config = ModelConfig(development_config="nonexistent.yaml")
    assert config.get("llm_parameters").get("temperature") == 0.01


@mock.patch("mlflow.langchain._rag_utils")
def test_config_setup_with_mlflow_langchain_path(mock_rag_config_path):
    mock_rag_config_path.__databricks_rag_config_path__ = VALID_CONFIG_PATH_2
    config = ModelConfig(development_config=VALID_CONFIG_PATH)
    # here the config.yaml has the max_tokens set to 500
    # where as the config_2.yaml has it set to 200.
    # Here we give preference to the __databricks_rag_config_path__.
    assert config.get("llm_parameters").get("max_tokens") == 200


def test_config_development_config_must_be_specified_with_keyword():
    with pytest.raises(TypeError, match="1 positional argument but 2 were given"):
        ModelConfig(VALID_CONFIG_PATH_2)
