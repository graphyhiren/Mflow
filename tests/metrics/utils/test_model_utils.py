from unittest import mock

import pytest
from aiohttp import ClientTimeout

from mlflow.gateway.constants import MLFLOW_GATEWAY_ROUTE_TIMEOUT_SECONDS
from mlflow.metrics.utils.model_utils import (
    _parse_model_uri,
    score_model_on_payload,
)

from tests.gateway.tools import MockAsyncResponse, mock_http_client


@pytest.fixture
def set_envs(monkeypatch):
    monkeypatch.setenvs(
        {
            "MLFLOW_TESTING": "true",
            "OPENAI_API_KEY": "test",
            "SERPAPI_API_KEY": "test",
        }
    )


def test_parse_model_uri():
    prefix, suffix = _parse_model_uri("openai:/gpt-3.5-turbo")

    assert prefix == "openai"
    assert suffix == "gpt-3.5-turbo"

    prefix, suffix = _parse_model_uri("model:/123")

    assert prefix == "model"
    assert suffix == "123"

    prefix, suffix = _parse_model_uri("gateway:/my-route")

    assert prefix == "gateway"
    assert suffix == "my-route"


def test_parse_model_uri_throws_for_malformed():
    with pytest.raises(ValueError):
        _parse_model_uri("gpt-3.5-turbo")


def test_score_model_on_payload_throws_for_invalid():
    with pytest.raises(ValueError):
        score_model_on_payload("gpt-3.5-turbo", {})


def test_score_model_openai_without_key():
    with pytest.raises(ValueError):
        score_model_on_payload("openai:/gpt-3.5-turbo", {})


def test_score_model_openai(set_envs):
    resp = {
        "id": "chatcmpl-abc123",
        "object": "chat.completion",
        "created": 1677858242,
        "model": "gpt-3.5-turbo-0301",
        "usage": {
            "prompt_tokens": 13,
            "completion_tokens": 7,
            "total_tokens": 20,
        },
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "\n\nThis is a test!",
                },
                "finish_reason": "stop",
                "index": 0,
            }
        ],
        "headers": {"Content-Type": "application/json"},
    }
    mock_client = mock_http_client(MockAsyncResponse(resp))

    with mock.patch("aiohttp.ClientSession", return_value=mock_client):
        score_model_on_payload("openai:/gpt-3.5-turbo", {"prompt": "my prompt", "temperature": 0.1})
        mock_client.post.assert_called_once_with(
            "https://api.openai.com/v1/chat/completions",
            json={
                "model": "gpt-3.5-turbo",
                "temperature": 0.2,
                "messages": [{"role": "user", "content": "my prompt"}],
            },
            timeout=ClientTimeout(total=MLFLOW_GATEWAY_ROUTE_TIMEOUT_SECONDS),
        )


def test_score_model_gateway():
    expected_output = {
        "candidates": [
            {
                "message": {
                    "role": "assistant",
                    "content": "The core of the sun is estimated to have a temperature of about "
                    "15 million degrees Celsius (27 million degrees Fahrenheit).",
                },
                "metadata": {"finish_reason": "stop"},
            }
        ],
        "metadata": {
            "input_tokens": 17,
            "output_tokens": 24,
            "total_tokens": 41,
            "model": "gpt-3.5-turbo-0301",
            "route_type": "llm/v1/chat",
        },
    }

    with mock.patch("mlflow.gateway.query", return_value=expected_output):
        response = score_model_on_payload("gateway:/my-route", {})
        assert response == expected_output
