from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from mlflow.utils.annotations import experimental

DATABRICKS_VECTOR_SEARCH_PRIMARY_KEY = "__databricks_vector_search_primary_key__"
DATABRICKS_VECTOR_SEARCH_TEXT_COLUMN = "__databricks_vector_search_text_column__"
DATABRICKS_VECTOR_SEARCH_DOC_URI = "__databricks_vector_search_doc_uri__"
DATABRICKS_VECTOR_SEARCH_OTHER_COLUMNS = "__databricks_vector_search_other_columns__"


@experimental
def set_vector_search_schema(
    primary_key: str,
    text_column: str = "",
    doc_uri: Optional[str] = None,
    other_columns: Optional[List[str]] = None,
):
    """
    After defining your vector store in a Python file or notebook, call
    set_vector_search_schema() so that we can correctly map the vector index
    columns. These columns would be used during tracing and in the review UI.

    Args:
        primary_key: The primary key of the vector index.
        text_column: The name of the text column to use for the embeddings.
        doc_uri: The name of the column that contains the document URI.
        other_columns: A list of other columns that are part of the vector index
                          that need to be retrieved during trace logging.
        Note: Make sure the text column specified is in the index.

        Example:

        .. code-block:: python

            from mlflow.models import set_vector_search_schema

            set_vector_search_schema(
                primary_key="chunk_id",
                text_column="chunk_text",
                doc_uri="doc_uri",
                other_columns=["title"],
            )
    """
    globals()[DATABRICKS_VECTOR_SEARCH_PRIMARY_KEY] = primary_key
    globals()[DATABRICKS_VECTOR_SEARCH_TEXT_COLUMN] = text_column
    globals()[DATABRICKS_VECTOR_SEARCH_DOC_URI] = doc_uri
    globals()[DATABRICKS_VECTOR_SEARCH_OTHER_COLUMNS] = other_columns or []


def _get_vector_search_schema():
    """
    Get the vector search schema defined by the user.

    Returns:
        VectorSearchIndex: The vector search index schema.
    """
    return VectorSearchIndex(
        name="vector_search_index",
        primary_key=globals().get(DATABRICKS_VECTOR_SEARCH_PRIMARY_KEY),
        text_column=globals().get(DATABRICKS_VECTOR_SEARCH_TEXT_COLUMN),
        doc_uri=globals().get(DATABRICKS_VECTOR_SEARCH_DOC_URI),
        other_columns=globals().get(DATABRICKS_VECTOR_SEARCH_OTHER_COLUMNS),
    )


class DependenciesType(Enum):
    """
    Enum to define the different types of dependencies of the model.
    """

    VECTOR_SEARCH_INDEX = "vector_search_index"


@dataclass
class Schema(ABC):
    """
    Base class for defining the resources needed to serve a model.

    Args:
        type (DependenciesType): The type of the schema.
    """

    type: DependenciesType

    @abstractmethod
    def to_dict(self):
        """
        Convert the resource to a dictionary.
        Subclasses must implement this method.
        """

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, str]):
        """
        Convert the dictionary to a Resource.
        Subclasses must implement this method.
        """


@dataclass
class VectorSearchIndex(Schema):
    """
    Define vector search index resource to serve a model.

    Args:
        name (str): The name of the vector searcg schema.
        primary_key (str): The primary key for the index.
        text_column (str): The main text column for the index.
        doc_uri (Optional[str]): The document URI for the index.
        other_columns (Optional[List[str]]): Additional columns in the index.
    """

    type: DependenciesType = DependenciesType.VECTOR_SEARCH_INDEX
    name: str = None
    primary_key: str = None
    text_column: str = None
    doc_uri: Optional[str] = None
    other_columns: Optional[List[str]] = field(default_factory=list)

    def to_dict(self):
        return {
            self.type.value: [
                {
                    "name": self.name,
                    "primary_key": self.primary_key,
                    "text_column": self.text_column,
                    "doc_uri": self.doc_uri,
                    "other_columns": self.other_columns,
                }
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]):
        return cls(
            name=data["name"],
            primary_key=data["primary_key"],
            text_column=data["text_column"],
            doc_uri=data.get("doc_uri"),
            other_columns=data.get("other_columns", []),
        )


@dataclass
class DependenciesSchemas:
    vector_search_index: List[VectorSearchIndex] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Dict[DependenciesType, List[Dict]]]:
        return {
            "dependencies_schemas": {
                DependenciesType.VECTOR_SEARCH_INDEX.value: [
                    index.to_dict()[DependenciesType.VECTOR_SEARCH_INDEX.value][0]
                    for index in self.vector_search_index
                ],
            }
        }
