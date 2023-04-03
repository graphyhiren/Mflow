from typing import TypeVar, Any, Optional, Dict

from mlflow.data.dataset_source import DatasetSource
from mlflow.exceptions import MlflowException
from mlflow.protos.databricks_pb2 import INVALID_PARAMETER_VALUE
from pyspark.sql import SparkSession, DataFrame


SparkDatasetSourceType = TypeVar("SparkDatasetSourceType", bound="SparkDatasetSource")


class SparkDatasetSource(DatasetSource):
    def __init__(
        self,
        path: Optional[str] = None,
        table_name: Optional[str] = None,
        sql: Optional[str] = None,
    ):
        if (path, table_name, sql).count(None) != 2:
            raise MlflowException(
                'Must specify exactly one of "path", "table_name", and "sql"',
                INVALID_PARAMETER_VALUE,
            )
        self._path = path
        self._table_name = table_name
        self._sql = sql

    @staticmethod
    def _get_source_type() -> str:
        return "spark"

    def load(self, **kwargs) -> DataFrame:
        """
        Loads the dataset source as a Hugging Face Dataset or DatasetDict, depending on whether
        multiple splits are defined by the source or not.
        :param kwargs: Additional keyword arguments used for loading the dataset with
                       the Hugging Face `datasets.load_dataset()` method. The following keyword
                       arguments are used automatically from the dataset source but may be overriden
                       by values passed in **kwargs: path, name, data_dir, data_files, split,
                       revision, task.
        :throws: MlflowException if the Spark dataset source does not define a path
                 from which to load the data.
        :return: An instance of `pyspark.sql.DataFrame`.
        """
        spark = SparkSession.builder.getOrCreate()

        # TODO: read from self.table_name and sql
        if self._path:
            return spark.read.parquet(self._path)
        if self._table_name:
            return spark.read.table(self._table_name)

    @staticmethod
    def _can_resolve(raw_source: Any):
        return False

    @classmethod
    def _resolve(cls, raw_source: str) -> SparkDatasetSourceType:
        raise NotImplementedError

    def _to_dict(self) -> Dict[Any, Any]:
        return {
            "path": self._path,
        }

    @classmethod
    def _from_dict(cls, source_dict: Dict[Any, Any]) -> SparkDatasetSourceType:
        return cls(
            path=source_dict.get("path"),
        )
