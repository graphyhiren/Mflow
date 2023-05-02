import json
import logging
from typing import Optional, Any, Dict, Union

import tensorflow as tf
from functools import cached_property

from mlflow.data.dataset import Dataset
from mlflow.data.dataset_source import DatasetSource
from mlflow.data.digest_utils import compute_tensor_digest, compute_tensorflow_dataset_digest
from mlflow.data.pyfunc_dataset_mixin import PyFuncConvertibleDatasetMixin, PyFuncInputsOutputs
from mlflow.exceptions import MlflowException
from mlflow.models.evaluation.base import EvaluationDataset
from mlflow.types import Schema
from mlflow.types.utils import _infer_schema
from mlflow.utils.annotations import experimental

_logger = logging.getLogger(__name__)


@experimental
class TensorFlowDataset(Dataset, PyFuncConvertibleDatasetMixin):
    """
    Represents a TensorFlow dataset for use with MLflow Tracking.
    """

    def __init__(
        self,
        data: Union[tf.data.Dataset, tf.Tensor],
        source: DatasetSource,
        targets=None,
        name: Optional[str] = None,
        digest: Optional[str] = None,
    ):
        """
        :param source: The source of the TensorFlow dataset.
        :param data: An instance of ``tf.data.Dataset`` or ``tf.Tensor``.
        :param source: The source of the TensorFlow dataset.
        :param targets: A TensorFlow dataset or tensor containing dataset targets. Optional
        :param name: The name of the dataset. E.g. "wiki_train". If unspecified, a name is
                     automatically generated.
        :param digest: The digest (hash, fingerprint) of the dataset. If unspecified, a digest
                       is automatically computed.
        """
        self._data = data
        self._targets = targets
        super().__init__(source=source, name=name, digest=digest)

    def _compute_digest(self) -> str:
        """
        Computes a digest for the dataset. Called if the user doesn't supply
        a digest when constructing the dataset.
        """
        return (
            compute_tensorflow_dataset_digest(self._data, self._targets)
            if isinstance(self._data, tf.data.Dataset)
            else compute_tensor_digest(self._data, self._targets)
        )

    def _to_dict(self, base_dict: Dict[str, str]) -> Dict[str, str]:
        """
        :param base_dict: A string dictionary of base information about the
                          dataset, including: name, digest, source, and source
                          type.
        :return: A string dictionary containing the following fields: name,
                 digest, source, source type, schema (optional), profile
                 (optional).
        """
        base_dict.update(
            {
                "schema": json.dumps({"mlflow_tensorspec": self.schema.to_dict()})
                if self.schema
                else None,
                "profile": json.dumps(self.profile),
            }
        )
        return base_dict

    @property
    def data(self):
        """
        The underlying TensorFlow data.
        """
        return self._data

    @property
    def source(self) -> DatasetSource:
        """
        The source of the dataset.
        """
        return self._source

    @property
    def targets(self):
        """
        The targets of the dataset.
        """
        return self._targets

    @property
    def profile(self) -> Optional[Any]:
        """
        A profile of the dataset. May be None if no profile is available.
        """
        profile = {
            "features_num_rows": len(self._data),
            "features_num_elements": int(self._data.cardinality().numpy())
            if isinstance(self._data, tf.data.Dataset)
            else int(tf.size(self._data).numpy()),
        }
        if self._targets is not None:
            profile.update(
                {
                    "targets_num_rows": len(self._targets),
                    "targets_num_elements": int(self._targets.cardinality().numpy())
                    if isinstance(self._targets, tf.data.Dataset)
                    else int(tf.size(self._targets).numpy()),
                }
            )
        return profile

    @cached_property
    def schema(self) -> Optional[Schema]:
        """
        An MLflow TensorSpec schema representing the tensor dataset
        """
        try:
            if isinstance(self._data, tf.data.Dataset):
                features_tensor = next(self._data.as_numpy_iterator())
                if isinstance(features_tensor, tuple):
                    features_tensor = features_tensor[0]
            else:
                features_tensor = self._data.numpy()

            schema_dict = {"features": features_tensor}
            if self._targets is not None:
                if isinstance(self._targets, tf.data.Dataset):
                    targets_tensor = next(self._targets.as_numpy_iterator())
                    if isinstance(targets_tensor, tuple):
                        targets_tensor = targets_tensor[0]
                else:
                    targets_tensor = self._targets.numpy()
                schema_dict["targets"] = targets_tensor
            return _infer_schema(schema_dict)
        except Exception as e:
            _logger.warning("Failed to infer schema for TensorFlow dataset. Exception: %s", e)
            return None

    def to_pyfunc(self) -> PyFuncInputsOutputs:
        """
        Converts the dataset to a collection of pyfunc inputs and outputs for model
        evaluation. Required for use with mlflow.evaluate().
        """
        return PyFuncInputsOutputs(self._data, self._targets)

    def to_evaluation_dataset(self, path=None, feature_names=None) -> EvaluationDataset:
        """
        Converts the dataset to an EvaluationDataset for model evaluation. Only supported if the
        dataset is a Tensor. Required for use with mlflow.evaluate().
        """
        # check that data and targets are Tensors
        if not isinstance(self._data, tf.Tensor):
            raise MlflowException("Data must be a Tensor to convert to an EvaluationDataset.")
        if self._targets is not None and not isinstance(self._targets, tf.Tensor):
            raise MlflowException("Targets must be a Tensor to convert to an EvaluationDataset.")
        return EvaluationDataset(
            data=self._data.numpy(),
            targets=self._targets.numpy() if self._targets is not None else None,
            path=path,
            feature_names=feature_names,
        )


def from_tensorflow(
    data: Union[tf.data.Dataset, tf.Tensor],
    source: Optional[Union[str, DatasetSource]] = None,
    targets=None,
    name: Optional[str] = None,
    digest: Optional[str] = None,
) -> TensorFlowDataset:
    """
    Constructs a :py:class`TensorFlowDataset` object from TensorFlow data, optional targets, and
    source. If the source is path like, then this will construct a DatasetSource object from the
    source path. Otherwise, the source is assumed to be a DatasetSource object.

    :param data: An instance of ``tf.data.Dataset`` or ``tf.Tensor``.
    :param source: The source from which the data was derived, e.g. a filesystem
                    path, an S3 URI, an HTTPS URL, a delta table name with version, or
                    spark table etc. If source is not a path like string,
                    pass in a DatasetSource object directly. If no source is specified,
                    a CodeDatasetSource is used, which will source information from the run
                    context.
    :param targets: A TensorFlow dataset or TensorFlow tensor containing dataset targets.
    :param name: The name of the dataset. If unspecified, a name is generated.
    :param digest: A dataset digest (hash). If unspecified, a digest is computed
                    automatically.
    """
    from mlflow.data.code_dataset_source import CodeDatasetSource
    from mlflow.data.dataset_source_registry import resolve_dataset_source
    from mlflow.tracking.context import registry

    if source is not None:
        if isinstance(source, DatasetSource):
            resolved_source = source
        else:
            resolved_source = resolve_dataset_source(
                source,
            )
    else:
        context_tags = registry.resolve_tags()
        resolved_source = CodeDatasetSource(tags=context_tags)
    return TensorFlowDataset(
        data=data, source=resolved_source, targets=targets, name=name, digest=digest
    )
