from typing import Any
from unittest import mock

import pytest

from mlflow.data.dataset_source_registry import DatasetSourceRegistry
from mlflow.exceptions import MlflowException

from tests.resources.data.dataset_source import TestDatasetSource


def test_register_entrypoints_and_resolve(tmp_path):
    """This test requires the package in tests/resources/mlflow-test-plugin to be installed"""

    from mlflow_test_plugin.dummy_dataset_source import DummyDatasetSource

    registry = DatasetSourceRegistry()
    registry.register_entrypoints()

    uri = "dummy:" + str(tmp_path)
    resolved_source = registry.resolve(uri)
    assert isinstance(resolved_source, DummyDatasetSource)
    # Verify that the DummyDatasetSource is constructed with the correct URI
    assert resolved_source.uri == uri


def test_register_dataset_source_and_resolve(tmp_path):
    registry = DatasetSourceRegistry()
    registry.register(TestDatasetSource)

    uri = "test:" + str(tmp_path)
    resolved_source = registry.resolve(uri)
    assert isinstance(resolved_source, TestDatasetSource)
    # Verify that the TestDatasetSource is constructed with the correct URI
    assert resolved_source.uri == uri


def test_register_dataset_source_and_load_from_json(tmp_path):
    registry = DatasetSourceRegistry()
    registry.register(TestDatasetSource)
    resolved_source = registry.resolve("test:" + str(tmp_path))
    resolved_source_json = resolved_source.to_json()
    source_from_json = registry.get_source_from_json(
        source_json=resolved_source_json, source_type="test"
    )
    assert source_from_json.uri == resolved_source.uri


def test_load_from_json_throws_for_unrecognized_source_type(tmp_path):
    registry = DatasetSourceRegistry()
    registry.register(TestDatasetSource)

    with pytest.raises(MlflowException, match="unrecognized source type: foo"):
        registry.get_source_from_json(source_json='{"bar": "123"}', source_type="foo")

    class CandidateDatasetSource1(TestDatasetSource):
        @staticmethod
        def _get_source_type() -> str:
            return "candidate1"

        @staticmethod
        def _can_resolve(raw_source: Any) -> bool:
            return raw_source.startswith("candidate1")

    class CandidateDatasetSource2(CandidateDatasetSource1):
        @staticmethod
        def _get_source_type() -> str:
            return "candidate2"

        @staticmethod
        def _can_resolve(raw_source: Any) -> bool:
            return raw_source.startswith("candidate2")

    registry = DatasetSourceRegistry()
    registry.register(TestDatasetSource)
    registry.register(CandidateDatasetSource1)
    registry.register(CandidateDatasetSource2)

    registry.resolve("test:" + str(tmp_path))
    registry.resolve("test:" + str(tmp_path), candidate_sources=[TestDatasetSource])
    with pytest.raises(MlflowException, match="Could not find a source information resolver"):
        # TestDatasetSource is the only source that can resolve raw sources with scheme "test",
        # and TestDatasetSource is not a subclass of CandidateDatasetSource1
        registry.resolve("test:" + str(tmp_path), candidate_sources=[CandidateDatasetSource1])

    registry.resolve("candidate1:" + str(tmp_path))
    registry.resolve("candidate1:" + str(tmp_path), candidate_sources=[CandidateDatasetSource1])
    # CandidateDatasetSource1 is a subclass of TestDatasetSource and is therefore considered
    # as a candidate for resolution
    registry.resolve("candidate1:" + str(tmp_path), candidate_sources=[TestDatasetSource])
    with pytest.raises(MlflowException, match="Could not find a source information resolver"):
        # CandidateDatasetSource2 is not a superclass of CandidateDatasetSource1 or
        # TestDatasetSource and cannot resolve raw sources with scheme "candidate1"
        registry.resolve("candidate1:" + str(tmp_path), candidate_sources=[CandidateDatasetSource2])


def test_resolve_dataset_source_maintains_consistent_order_and_uses_last_registered_match(tmp_path):
    """This test requires the package in tests/resources/mlflow-test-plugin to be installed"""

    from mlflow_test_plugin.dummy_dataset_source import DummyDatasetSource

    class TestDatasetSourceCopy1(TestDatasetSource):
        pass

    class TestDatasetSourceCopy2(TestDatasetSource):
        pass

    registry1 = DatasetSourceRegistry()
    registry1.register(TestDatasetSource)
    registry1.register(TestDatasetSourceCopy1)
    registry1.register(TestDatasetSourceCopy2)
    source1 = registry1.resolve("test:/" + str(tmp_path))
    assert isinstance(source1, TestDatasetSourceCopy2)

    registry2 = DatasetSourceRegistry()
    registry2.register(TestDatasetSource)
    registry2.register(TestDatasetSourceCopy2)
    registry2.register(TestDatasetSourceCopy1)
    source2 = registry2.resolve("test:/" + str(tmp_path))
    assert isinstance(source2, TestDatasetSourceCopy1)

    # Verify that a different matching dataset source can still be resolved via `candidates`
    source3 = registry2.resolve(
        "test:/" + str(tmp_path), candidate_sources=[TestDatasetSourceCopy2]
    )
    assert isinstance(source3, TestDatasetSourceCopy2)

    # Verify that last registered order applies to entrypoints too
    class DummyDatasetSourceCopy(DummyDatasetSource):
        pass

    registry3 = DatasetSourceRegistry()
    registry3.register(DummyDatasetSourceCopy)
    source4 = registry3.resolve("dummy:/" + str(tmp_path))
    assert isinstance(source4, DummyDatasetSourceCopy)
    registry3.register_entrypoints()
    source5 = registry3.resolve("dummy:/" + str(tmp_path))
    assert isinstance(source5, DummyDatasetSource)


def test_resolve_dataset_source_warns_when_multiple_matching_sources_found(tmp_path):
    class TestDatasetSourceCopy1(TestDatasetSource):
        pass

    class TestDatasetSourceCopy2(TestDatasetSource):
        pass

    registry1 = DatasetSourceRegistry()
    registry1.register(TestDatasetSource)
    registry1.register(TestDatasetSourceCopy1)
    registry1.register(TestDatasetSourceCopy2)

    with mock.patch("mlflow.data.dataset_source_registry.warnings.warn") as mock_warn:
        registry1.resolve("test:/" + str(tmp_path))
        mock_warn.assert_called_once()
        call_args, _ = mock_warn.call_args
        multiple_match_msg = call_args[0]
        assert (
            "The specified dataset source can be interpreted in multiple ways" in multiple_match_msg
        )
        assert (
            "TestDatasetSource, TestDatasetSourceCopy1, TestDatasetSourceCopy2"
            in multiple_match_msg
        )
        assert (
            "MLflow will assume that this is a TestDatasetSourceCopy2 source" in multiple_match_msg
        )


def test_dataset_sources_are_importable_from_sources_module(tmp_path):
    from mlflow.data.sources import LocalArtifactDatasetSource

    src = LocalArtifactDatasetSource(tmp_path)
    assert src._get_source_type() == "local"
    assert src.uri == tmp_path

    from mlflow.data.sources import DeltaDatasetSource

    src = DeltaDatasetSource(path=tmp_path)
    assert src._get_source_type() == "delta_table"
    assert src.path == tmp_path
