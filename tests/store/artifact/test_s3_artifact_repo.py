import json
import os
import posixpath
import tarfile
from datetime import datetime
from unittest import mock
from unittest.mock import ANY

import pytest

from mlflow.protos.service_pb2 import FileInfo
from mlflow.store.artifact.artifact_repository_registry import get_artifact_repository
from mlflow.store.artifact.s3_artifact_repo import (
    _MAX_CACHE_SECONDS,
    S3ArtifactRepository,
    _cached_get_s3_client,
)
from mlflow.store.artifact.optimized_s3_artifact_repo import OptimizedS3ArtifactRepository

from tests.helper_functions import set_boto_credentials  # noqa: F401


@pytest.fixture
def s3_artifact_root(mock_s3_bucket):
    return f"s3://{mock_s3_bucket}"


@pytest.fixture(params=[True, False])
def s3_artifact_repo(s3_artifact_root, request):
    if request.param:
        return OptimizedS3ArtifactRepository(posixpath.join(s3_artifact_root, "some/path"))
    return S3ArtifactRepository(posixpath.join(s3_artifact_root, "some/path"))


@pytest.fixture(autouse=True)
def reset_cached_get_s3_client():
    _cached_get_s3_client.cache_clear()


def teardown_function():
    if "MLFLOW_S3_UPLOAD_EXTRA_ARGS" in os.environ:
        del os.environ["MLFLOW_S3_UPLOAD_EXTRA_ARGS"]


def test_file_artifact_is_logged_and_downloaded_successfully(s3_artifact_repo, tmp_path):
    file_name = "test.txt"
    file_path = os.path.join(tmp_path, file_name)
    file_text = "Hello world!"

    with open(file_path, "w") as f:
        f.write(file_text)

    repo = s3_artifact_repo
    repo.log_artifact(file_path)
    downloaded_text = open(repo.download_artifacts(file_name)).read()
    assert downloaded_text == file_text


def test_file_artifact_is_logged_with_content_metadata(
    s3_artifact_repo, s3_artifact_root, tmp_path
):
    file_name = "test.txt"
    file_path = os.path.join(tmp_path, file_name)
    file_text = "Hello world!"

    with open(file_path, "w") as f:
        f.write(file_text)

    repo = s3_artifact_repo
    repo.log_artifact(file_path)

    bucket, _ = repo.parse_s3_compliant_uri(s3_artifact_root)
    s3_client = repo._get_s3_client()
    response = s3_client.head_object(Bucket=bucket, Key="some/path/test.txt")
    assert response.get("ContentType") == "text/plain"
    assert response.get("ContentEncoding") is None


def test_get_s3_client_hits_cache(s3_artifact_root, monkeypatch):
    # pylint: disable=no-value-for-parameter
    repo = get_artifact_repository(posixpath.join(s3_artifact_root, "some/path"))
    repo._get_s3_client()
    cache_info = _cached_get_s3_client.cache_info()
    assert cache_info.hits == 0
    assert cache_info.misses == 1
    assert cache_info.currsize == 1

    repo._get_s3_client()
    cache_info = _cached_get_s3_client.cache_info()
    assert cache_info.hits == 1
    assert cache_info.misses == 1
    assert cache_info.currsize == 1

    monkeypatch.setenv("MLFLOW_EXPERIMENTAL_S3_SIGNATURE_VERSION", "s3v2")
    repo._get_s3_client()
    cache_info = _cached_get_s3_client.cache_info()
    assert cache_info.hits == 1
    assert cache_info.misses == 2
    assert cache_info.currsize == 2

    with mock.patch(
        "mlflow.store.artifact.s3_artifact_repo._get_utcnow_timestamp",
        return_value=datetime.utcnow().timestamp() + _MAX_CACHE_SECONDS,
    ):
        repo._get_s3_client()
    cache_info = _cached_get_s3_client.cache_info()
    assert cache_info.hits == 1
    assert cache_info.misses == 3
    assert cache_info.currsize == 3


@pytest.mark.parametrize(
    ("ignore_tls_env", "verify"), [("0", None), ("1", False), ("true", False), ("false", None)]
)
def test_get_s3_client_verify_param_set_correctly(
    s3_artifact_root, ignore_tls_env, verify, monkeypatch
):
    monkeypatch.setenv("MLFLOW_S3_IGNORE_TLS", ignore_tls_env)
    with mock.patch("boto3.client") as mock_get_s3_client:
        repo = get_artifact_repository(posixpath.join(s3_artifact_root, "some/path"))
        repo._get_s3_client()
        mock_get_s3_client.assert_called_with(
            "s3",
            config=ANY,
            endpoint_url=ANY,
            verify=verify,
            aws_access_key_id=None,
            aws_secret_access_key=None,
            aws_session_token=None,
            region_name=ANY,
        )


def test_s3_client_config_set_correctly(s3_artifact_root):
    repo = get_artifact_repository(posixpath.join(s3_artifact_root, "some/path"))
    s3_client = repo._get_s3_client()
    assert s3_client.meta.config.s3.get("addressing_style") == "path"


def test_s3_creds_passed_to_client(s3_artifact_root):
    with mock.patch("boto3.client") as mock_get_s3_client:
        repo = S3ArtifactRepository(
            s3_artifact_root,
            access_key_id="my-id",
            secret_access_key="my-key",
            session_token="my-session-token",
        )
        repo._get_s3_client()
        mock_get_s3_client.assert_called_with(
            "s3",
            config=ANY,
            endpoint_url=ANY,
            verify=None,
            aws_access_key_id="my-id",
            aws_secret_access_key="my-key",
            aws_session_token="my-session-token",
            region_name=ANY,
        )


def test_file_artifacts_are_logged_with_content_metadata_in_batch(
    s3_artifact_repo, s3_artifact_root, tmp_path
):
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    subdir_path = str(subdir)
    nested_path = os.path.join(subdir_path, "nested")
    os.makedirs(nested_path)
    path_a = os.path.join(subdir_path, "a.txt")
    path_b = os.path.join(subdir_path, "b.tar.gz")
    path_c = os.path.join(nested_path, "c.csv")

    with open(path_a, "w") as f:
        f.write("A")
    with tarfile.open(path_b, "w:gz") as f:
        f.add(path_a)
    with open(path_c, "w") as f:
        f.write("col1,col2\n1,3\n2,4\n")

    repo = s3_artifact_repo
    repo.log_artifacts(subdir_path)

    bucket, _ = repo.parse_s3_compliant_uri(s3_artifact_root)
    s3_client = repo._get_s3_client()

    response_a = s3_client.head_object(Bucket=bucket, Key="some/path/a.txt")
    assert response_a.get("ContentType") == "text/plain"
    assert response_a.get("ContentEncoding") is None

    response_b = s3_client.head_object(Bucket=bucket, Key="some/path/b.tar.gz")
    assert response_b.get("ContentType") == "application/x-tar"
    assert response_b.get("ContentEncoding") == "gzip"

    response_c = s3_client.head_object(Bucket=bucket, Key="some/path/nested/c.csv")
    assert response_c.get("ContentType") == "text/csv"
    assert response_c.get("ContentEncoding") is None


def test_file_and_directories_artifacts_are_logged_and_downloaded_successfully_in_batch(
    s3_artifact_repo, tmp_path
):
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    subdir_path = str(subdir)
    nested_path = os.path.join(subdir_path, "nested")
    os.makedirs(nested_path)
    with open(os.path.join(subdir_path, "a.txt"), "w") as f:
        f.write("A")
    with open(os.path.join(subdir_path, "b.txt"), "w") as f:
        f.write("B")
    with open(os.path.join(nested_path, "c.txt"), "w") as f:
        f.write("C")

    repo = s3_artifact_repo
    repo.log_artifacts(subdir_path)

    # Download individual files and verify correctness of their contents
    downloaded_file_a_text = open(repo.download_artifacts("a.txt")).read()
    assert downloaded_file_a_text == "A"
    downloaded_file_b_text = open(repo.download_artifacts("b.txt")).read()
    assert downloaded_file_b_text == "B"
    downloaded_file_c_text = open(repo.download_artifacts("nested/c.txt")).read()
    assert downloaded_file_c_text == "C"

    # Download the nested directory and verify correctness of its contents
    downloaded_dir = repo.download_artifacts("nested")
    assert os.path.basename(downloaded_dir) == "nested"
    text = open(os.path.join(downloaded_dir, "c.txt")).read()
    assert text == "C"

    # Download the root directory and verify correctness of its contents
    downloaded_dir = repo.download_artifacts("")
    dir_contents = os.listdir(downloaded_dir)
    assert "nested" in dir_contents
    assert os.path.isdir(os.path.join(downloaded_dir, "nested"))
    assert "a.txt" in dir_contents
    assert "b.txt" in dir_contents


def test_file_and_directories_artifacts_are_logged_and_listed_successfully_in_batch(
    s3_artifact_repo, tmp_path
):
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    subdir_path = str(subdir)
    nested_path = os.path.join(subdir_path, "nested")
    os.makedirs(nested_path)
    with open(os.path.join(subdir_path, "a.txt"), "w") as f:
        f.write("A")
    with open(os.path.join(subdir_path, "b.txt"), "w") as f:
        f.write("B")
    with open(os.path.join(nested_path, "c.txt"), "w") as f:
        f.write("C")

    repo = s3_artifact_repo
    repo.log_artifacts(subdir_path)

    root_artifacts_listing = sorted(
        [(f.path, f.is_dir, f.file_size) for f in repo.list_artifacts()]
    )
    assert root_artifacts_listing == [
        ("a.txt", False, 1),
        ("b.txt", False, 1),
        ("nested", True, None),
    ]

    nested_artifacts_listing = sorted(
        [(f.path, f.is_dir, f.file_size) for f in repo.list_artifacts("nested")]
    )
    assert nested_artifacts_listing == [("nested/c.txt", False, 1)]


def test_download_directory_artifact_succeeds_when_artifact_root_is_s3_bucket_root(
    s3_artifact_root, tmp_path
):
    file_a_name = "a.txt"
    file_a_text = "A"
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    subdir_path = str(subdir)
    nested_path = os.path.join(subdir_path, "nested")
    os.makedirs(nested_path)
    with open(os.path.join(nested_path, file_a_name), "w") as f:
        f.write(file_a_text)

    repo = get_artifact_repository(s3_artifact_root)
    repo.log_artifacts(subdir_path)

    downloaded_dir_path = repo.download_artifacts("nested")
    assert file_a_name in os.listdir(downloaded_dir_path)
    with open(os.path.join(downloaded_dir_path, file_a_name)) as f:
        assert f.read() == file_a_text


def test_download_file_artifact_succeeds_when_artifact_root_is_s3_bucket_root(
    s3_artifact_root, tmp_path
):
    file_a_name = "a.txt"
    file_a_text = "A"
    file_a_path = os.path.join(tmp_path, file_a_name)
    with open(file_a_path, "w") as f:
        f.write(file_a_text)

    repo = get_artifact_repository(s3_artifact_root)
    repo.log_artifact(file_a_path)

    downloaded_file_path = repo.download_artifacts(file_a_name)
    with open(downloaded_file_path) as f:
        assert f.read() == file_a_text


def test_get_s3_file_upload_extra_args():
    os.environ.setdefault(
        "MLFLOW_S3_UPLOAD_EXTRA_ARGS",
        '{"ServerSideEncryption": "aws:kms", "SSEKMSKeyId": "123456"}',
    )

    parsed_args = S3ArtifactRepository.get_s3_file_upload_extra_args()

    assert parsed_args == {"ServerSideEncryption": "aws:kms", "SSEKMSKeyId": "123456"}


def test_get_s3_file_upload_extra_args_env_var_not_present():
    parsed_args = S3ArtifactRepository.get_s3_file_upload_extra_args()

    assert parsed_args is None


def test_get_s3_file_upload_extra_args_invalid_json():
    os.environ.setdefault(
        "MLFLOW_S3_UPLOAD_EXTRA_ARGS", '"ServerSideEncryption": "aws:kms", "SSEKMSKeyId": "123456"}'
    )

    with pytest.raises(json.decoder.JSONDecodeError, match=r".+"):
        S3ArtifactRepository.get_s3_file_upload_extra_args()


def test_delete_artifacts(s3_artifact_repo, tmp_path):
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    subdir_path = str(subdir)
    nested_path = os.path.join(subdir_path, "nested")
    os.makedirs(nested_path)
    path_a = os.path.join(subdir_path, "a.txt")
    path_b = os.path.join(subdir_path, "b.tar.gz")
    path_c = os.path.join(nested_path, "c.csv")

    with open(path_a, "w") as f:
        f.write("A")
    with tarfile.open(path_b, "w:gz") as f:
        f.add(path_a)
    with open(path_c, "w") as f:
        f.write("col1,col2\n1,3\n2,4\n")

    repo = s3_artifact_repo
    repo.log_artifacts(subdir_path)

    # confirm that artifacts are present
    artifact_file_names = [obj.path for obj in repo.list_artifacts()]
    assert "a.txt" in artifact_file_names
    assert "b.tar.gz" in artifact_file_names
    assert "nested" in artifact_file_names

    repo.delete_artifacts()
    tmpdir_objects = repo.list_artifacts()
    assert not tmpdir_objects
