import io
import pickle
from unittest import mock

import pytest

from mlflow.environment_variables import MLFLOW_TRACKING_URI
from mlflow.store._unity_catalog.registry.rest_store import UcModelRegistryStore
from mlflow.store.db.db_types import DATABASE_ENGINES
from mlflow.store.model_registry.rest_store import RestStore
from mlflow.store.model_registry.sqlalchemy_store import SqlAlchemyStore
from mlflow.tracking._model_registry.utils import _get_store, get_registry_uri, set_registry_uri
from mlflow.tracking.registry import UnsupportedModelRegistryStoreURIException

# Disable mocking tracking URI here, as we want to test setting the tracking URI via
# environment variable. See
# http://doc.pytest.org/en/latest/skipping.html#skip-all-test-functions-of-a-class-or-module
# and https://github.com/mlflow/mlflow/blob/master/CONTRIBUTING.md#writing-python-tests
# for more information.
pytestmark = pytest.mark.notrackingurimock


@pytest.fixture()
def reset_registry_uri():
    yield
    set_registry_uri(None)


def test_set_get_registry_uri():
    with mock.patch(
        "mlflow.tracking._model_registry.utils.get_tracking_uri"
    ) as get_tracking_uri_mock:
        get_tracking_uri_mock.return_value = "databricks://tracking_sldkfj"
        uri = "databricks://registry/path"
        set_registry_uri(uri)
        assert get_registry_uri() == uri
        set_registry_uri(None)


def test_set_get_empty_registry_uri():
    with mock.patch(
        "mlflow.tracking._model_registry.utils.get_tracking_uri"
    ) as get_tracking_uri_mock:
        get_tracking_uri_mock.return_value = None
        set_registry_uri("")
        assert get_registry_uri() is None
        set_registry_uri(None)


def test_default_get_registry_uri_no_tracking_uri():
    with mock.patch(
        "mlflow.tracking._model_registry.utils.get_tracking_uri"
    ) as get_tracking_uri_mock:
        get_tracking_uri_mock.return_value = None
        set_registry_uri(None)
        assert get_registry_uri() is None


def test_default_get_registry_uri_with_tracking_uri_set():
    tracking_uri = "databricks://tracking_werohoz"
    with mock.patch(
        "mlflow.tracking._model_registry.utils.get_tracking_uri"
    ) as get_tracking_uri_mock:
        get_tracking_uri_mock.return_value = tracking_uri
        set_registry_uri(None)
        assert get_registry_uri() == tracking_uri


def test_get_store_rest_store_from_arg(monkeypatch):
    monkeypatch.setenv(MLFLOW_TRACKING_URI.name, "https://my-tracking-server:5050")
    store = _get_store("http://some/path")
    assert isinstance(store, RestStore)
    assert store.get_host_creds().host == "http://some/path"


def test_fallback_to_tracking_store(monkeypatch):
    monkeypatch.setenv(MLFLOW_TRACKING_URI.name, "https://my-tracking-server:5050")
    store = _get_store()
    assert isinstance(store, RestStore)
    assert store.get_host_creds().host == "https://my-tracking-server:5050"
    assert store.get_host_creds().token is None


@pytest.mark.parametrize("db_type", DATABASE_ENGINES)
def test_get_store_sqlalchemy_store(db_type, monkeypatch):
    uri = f"{db_type}://hostname/database"
    monkeypatch.setenv(MLFLOW_TRACKING_URI.name, uri)
    monkeypatch.delenv("MLFLOW_SQLALCHEMYSTORE_POOLCLASS", raising=False)
    with mock.patch("sqlalchemy.create_engine") as mock_create_engine, mock.patch(
        "mlflow.store.db.utils._initialize_tables"
    ), mock.patch(
        "mlflow.store.model_registry.sqlalchemy_store.SqlAlchemyStore."
        "_verify_registry_tables_exist"
    ):
        store = _get_store()
        assert isinstance(store, SqlAlchemyStore)
        assert store.db_uri == uri

    mock_create_engine.assert_called_once_with(uri, pool_pre_ping=True)


@pytest.mark.parametrize("bad_uri", ["badsql://imfake", "yoursql://hi"])
def test_get_store_bad_uris(bad_uri, monkeypatch):
    monkeypatch.setenv(MLFLOW_TRACKING_URI.name, bad_uri)
    with pytest.raises(
        UnsupportedModelRegistryStoreURIException,
        match="Model registry functionality is unavailable",
    ):
        _get_store()


def test_get_store_caches_on_store_uri(tmp_path):
    store_uri_1 = f"sqlite:///{tmp_path.joinpath('store1.db')}"
    store_uri_2 = f"sqlite:///{tmp_path.joinpath('store2.db')}"

    store1 = _get_store(store_uri_1)
    store2 = _get_store(store_uri_1)
    assert store1 is store2

    store3 = _get_store(store_uri_2)
    store4 = _get_store(store_uri_2)
    assert store3 is store4

    assert store1 is not store3


@pytest.mark.parametrize("store_uri", ["databricks-uc", "databricks-uc://profile"])
def test_get_store_uc_registry_uri(store_uri):
    assert isinstance(_get_store(store_uri), UcModelRegistryStore)


def test_store_object_can_be_serialized_by_pickle():
    """
    This test ensures a store object generated by `_get_store` can be serialized by pickle
    to prevent issues such as https://github.com/mlflow/mlflow/issues/2954
    """
    pickle.dump(_get_store("https://example.com"), io.BytesIO())
    pickle.dump(_get_store("databricks"), io.BytesIO())
    # pickle.dump(_get_store(f"sqlite:///{tmpdir.strpath}/mlflow.db"), io.BytesIO())
    # This throws `AttributeError: Can't pickle local object 'create_engine.<locals>.connect'`
