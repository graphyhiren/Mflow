import importlib
import subprocess
import sys
import time

import openai
import pytest
import requests
from packaging.version import Version

import mlflow

from tests.helper_functions import get_safe_port

is_v1 = Version(mlflow.openai._get_openai_package_version()).major >= 1


@pytest.fixture(scope="module", autouse=True)
def mock_openai():
    port = get_safe_port()
    with subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "tests.openai.mock_openai:app",
            "--host",
            "localhost",
            "--port",
            str(port),
        ]
    ) as proc:
        base_url = f"http://localhost:{port}"
        for _ in range(3):
            try:
                resp = requests.get(f"{base_url}/health")
            except requests.ConnectionError:
                time.sleep(1)
                continue
            if resp.ok:
                break
        else:
            raise RuntimeError("Failed to start mock OpenAI server")

        yield base_url
        proc.kill()


@pytest.fixture(autouse=True)
def set_envs(monkeypatch, mock_openai):
    monkeypatch.setenvs(
        {
            "MLFLOW_TESTING": "true",
            "OPENAI_API_KEY": "test",
            "OPENAI_API_BASE": mock_openai,
        }
    )
    if is_v1:
        openai.base_url = mock_openai
    else:
        importlib.reload(openai)
