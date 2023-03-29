import warnings

import datasets

from typing import TypeVar, Any, Union, Optional, Mapping, Sequence, Dict

from mlflow.exceptions import MlflowException
from mlflow.protos.databricks_pb2 import INVALID_PARAMETER_VALUE, RESOURCE_DOES_NOT_EXIST
from mlflow.store.artifact.artifact_repo import ArtifactRepository
from mlflow.store.artifact.artifact_repository_registry import _artifact_repository_registry

from mlflow.data.dataset_source import DatasetSource


HuggingFaceDatasetSourceType = TypeVar(
    "HuggingFaceDatasetSourceType", bound="HuggingFaceDatasetSource"
)


class HuggingFaceDatasetSource(DatasetSource):
    def __init__(
        self,
        builder_name: str,
        config_name: Optional[str] = None,
        data_dir: Optional[str] = None,
        data_files: Optional[
            Union[str, Sequence[str], Mapping[str, Union[str, Sequence[str]]]]
        ] = None,
        split: Optional[Union[str, datasets.Split]] = None,
        features: Optional[datasets.Features] = None,
        revision: Optional[Union[str, datasets.Version]] = None,
        task: Optional[Union[str, datasets.TaskTemplate]] = None,
    ):
        self._builder_name = builder_name
        self._config_name = config_name
        self._data_dir = data_dir
        self._data_files = data_files
        self._split = split
        self._features = features
        self._revision = revision
        self._task = task

    @staticmethod
    def _get_source_type() -> str:
        return "huggingface"

    def load(self, **kwargs) -> Union[datasets.Dataset, datasets.DatasetDict]:
        """
        Loads the dataset source as a Hugging Face Dataset or DatasetDict, depending on whether
        multiple splits are defined by the source or not.

        :param kwargs: Additional keyword arguments used for loading the dataset with
                       the Hugging Face `datasets.load_dataset()` method. The following keyword
                       arguments are used automatically from the dataset source but may be overriden
                       by values passed in **kwargs: path, name, data_dir, data_files, split,
                       features, revision, task.
        :throws: MlflowException if the Hugging Face dataset source does not define a path
                 from which to load the data.
        :return: An instance of `datasets.Dataset` or `datasets.DatasetDict`, depending on whether
                 multiple splits are defined by the source or not.
        """
        if self._builder_name is not None:
            raise MlflowException(
                "Could not load Hugging Face dataset source because the source does not define"
                " a dataset builder name (path).",
                RESOURCE_DOES_NOT_EXIST,
            )

        load_kwargs = {
            "path": self._builder_name,
            "name": self._config_name,
            "data_dir": self._data_dir,
            "data_files": self._data_files,
            "split": self._split,
            "features": self._features,
            "revision": self._revision,
            "task": self._task,
        }
        load_kwargs.update(kwargs)

        return datasets.load_dataset(**load_kwargs)

    @staticmethod
    def _can_resolve(raw_source: Any):
        # NB: Initially, we expect that Hugging Face dataset sources will only be used with
        # Hugging Face datasets constructed by from_huggingface_dataset, which can create
        # an instance of HuggingFaceDatasetSource directly without the need for resolution
        return False

    @classmethod
    def _resolve(cls, raw_source: str) -> HuggingFaceDatasetSourceType:
        raise NotImplementedError

    def _to_dict(self) -> Dict[str, Any]:
        return {
            "builder_name": self._builder_name,
            "config_name": self._config_name,
            "data_dir": self._data_dir,
            "data_files": self._data_files,
            "split": self._split,
            "features": self._features,
            "revision": self._revision,
            "task": self._task,
        }

    @classmethod
    def _from_dict(cls, source_dict: Dict[str, Any]) -> HuggingFaceDatasetSourceType:
        return cls(
            builder_name=source_dict.get("builder_name"),
            config_name=source_dict.get("config_name"),
            data_dir=source_dict.get("data_dir"),
            data_files=source_dict.get("data_files"),
            split=source_dict.get("split"),
            features=source_dict.get("features"),
            revision=source_dict.get("revision"),
            task=source_dict.get("task"),
        )
