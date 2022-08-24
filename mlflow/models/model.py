from datetime import datetime
import json
import logging
import warnings

import yaml
import os
import uuid

from typing import Any, Dict, Optional, Union, Callable

import mlflow
from mlflow.exceptions import MlflowException
from mlflow.tracking._model_registry import DEFAULT_AWAIT_MAX_SLEEP_SECONDS
from mlflow.utils.file_utils import TempDir
from mlflow.utils.databricks_utils import get_databricks_runtime

_logger = logging.getLogger(__name__)


MLMODEL_FILE_NAME = "MLmodel"
_LOG_MODEL_METADATA_WARNING_TEMPLATE = (
    "Logging model metadata to the tracking server has failed, possibly due older "
    "server version. The model artifacts have been logged successfully under %s. "
    "In addition to exporting model artifacts, MLflow clients 1.7.0 and above "
    "attempt to record model metadata to the tracking store. If logging to a "
    "mlflow server via REST, consider upgrading the server version to MLflow "
    "1.7.0 or above."
)
_MLFLOW_VERSION_KEY = "mlflow_version"


class ModelInfo:
    """
    The metadata of a logged MLflow Model.
    """

    def __init__(
        self,
        artifact_path: str = None,
        flavors: Dict[str, Any] = None,
        model_uri: str = None,
        model_uuid: str = None,
        run_id: str = None,
        saved_input_example_info: Optional[Dict[str, Any]] = None,
        signature_dict: Optional[Dict[str, Any]] = None,
        signature=None,  # Optional[ModelSignature]
        utc_time_created: str = None,
        mlflow_version: str = None,
    ):
        self._artifact_path = artifact_path
        self._flavors = flavors
        self._model_uri = model_uri
        self._model_uuid = model_uuid
        self._run_id = run_id
        self._saved_input_example_info = saved_input_example_info
        self._signature_dict = signature_dict
        self._signature = signature
        self._utc_time_created = utc_time_created
        self._mlflow_version = mlflow_version

    @property
    def artifact_path(self):
        """
        Run relative path identifying the logged model.
        """
        return self._artifact_path

    @property
    def flavors(self):
        """
        A dictionary mapping the flavor name to how to serve
        the model as that flavor. For example:

            .. code-block:: python

                {
                    "python_function": {
                        "model_path": "model.pkl",
                        "loader_module": "mlflow.sklearn",
                        "python_version": "3.8.10",
                        "env": "conda.yaml",
                    },
                    "sklearn": {
                        "pickled_model": "model.pkl",
                        "sklearn_version": "0.24.1",
                        "serialization_format": "cloudpickle",
                    },
                }
        """
        return self._flavors

    @property
    def model_uri(self):
        """
        The ``model_uri`` of the logged model in the format ``'runs:/<run_id>/<artifact_path>'``.
        """
        return self._model_uri

    @property
    def model_uuid(self):
        """
        The ``model_uuid`` of the logged model,
        e.g., ``'39ca11813cfc46b09ab83972740b80ca'``.
        """
        return self._model_uuid

    @property
    def run_id(self):
        """
        The ``run_id`` associated with the logged model,
        e.g., ``'8ede7df408dd42ed9fc39019ef7df309'``
        """
        return self._run_id

    @property
    def saved_input_example_info(self):
        """
        A dictionary that contains the metadata of the saved input example, e.g.,
        ``{"artifact_path": "input_example.json", "type": "dataframe", "pandas_orient": "split"}``.
        """
        return self._saved_input_example_info

    @property
    def signature_dict(self):
        """
        A dictionary that describes the model input and output generated by
        :py:meth:`ModelSignature.to_dict() <mlflow.models.ModelSignature.to_dict>`.
        """
        warnings.warn(
            "Field signature_dict is deprecated since v1.28.1. Use signature instead.",
            category=FutureWarning,
            stacklevel=2,
        )
        return self._signature_dict

    @signature_dict.setter
    def signature_dict(self, value):
        warnings.warn(
            "Field signature_dict is deprecated since v1.28.1. Use signature instead.",
            category=FutureWarning,
            stacklevel=2,
        )
        self._signature_dict = value

    @property
    def signature(self):  # -> Optional[ModelSignature]
        """
        A :py:class:`ModelSignature <mlflow.models.ModelSignature>` that describes the
        model input and output.
        """
        return self._signature

    @property
    def utc_time_created(self):
        """
        The UTC time that the logged model is created, e.g., ``'2022-01-12 05:17:31.634689'``.
        """
        return self._utc_time_created

    @property
    def mlflow_version(self):
        """
        Version of MLflow used to log the model
        """
        return self._mlflow_version


class Model:
    """
    An MLflow Model that can support multiple model flavors. Provides APIs for implementing
    new Model flavors.
    """

    def __init__(
        self,
        artifact_path=None,
        run_id=None,
        utc_time_created=None,
        flavors=None,
        signature=None,  # ModelSignature
        saved_input_example_info: Dict[str, Any] = None,
        model_uuid: Union[str, Callable, None] = lambda: uuid.uuid4().hex,
        mlflow_version: Union[str, None] = mlflow.version.VERSION,
        **kwargs,
    ):
        # store model id instead of run_id and path to avoid confusion when model gets exported
        if run_id:
            self.run_id = run_id
            self.artifact_path = artifact_path

        self.utc_time_created = str(utc_time_created or datetime.utcnow())
        self.flavors = flavors if flavors is not None else {}
        self.signature = signature
        self.saved_input_example_info = saved_input_example_info
        self.model_uuid = model_uuid() if callable(model_uuid) else model_uuid
        self.mlflow_version = mlflow_version
        self.__dict__.update(kwargs)

    def __eq__(self, other):
        if not isinstance(other, Model):
            return False
        return self.__dict__ == other.__dict__

    def get_input_schema(self):
        return self.signature.inputs if self.signature is not None else None

    def get_output_schema(self):
        return self.signature.outputs if self.signature is not None else None

    def load_input_example(self, path: str):
        """
        Load the input example saved along a model. Returns None if there is no example metadata
        (i.e. the model was saved without example). Raises FileNotFoundError if there is model
        metadata but the example file is missing.

        :param path: Path to the model directory.

        :return: Input example (NumPy ndarray, SciPy csc_matrix, SciPy csr_matrix,
                 pandas DataFrame, dict) or None if the model has no example.
        """

        # Just-in-time import to only load example-parsing libraries (e.g. numpy, pandas, etc.) if
        # example is requested.
        from mlflow.models.utils import _read_example

        return _read_example(self, path)

    def add_flavor(self, name, **params):
        """Add an entry for how to serve the model in a given format."""
        self.flavors[name] = params
        return self

    @property
    def signature(self):  # -> Optional[ModelSignature]
        return self._signature

    @signature.setter
    def signature(self, value):
        # pylint: disable=attribute-defined-outside-init
        self._signature = value

    @property
    def saved_input_example_info(self) -> Optional[Dict[str, Any]]:
        """
        A dictionary that contains the metadata of the saved input example, e.g.,
        ``{"artifact_path": "input_example.json", "type": "dataframe", "pandas_orient": "split"}``.
        """
        return self._saved_input_example_info

    @saved_input_example_info.setter
    def saved_input_example_info(self, value: Dict[str, Any]):
        # pylint: disable=attribute-defined-outside-init
        self._saved_input_example_info = value

    def get_model_info(self):
        """
        Create a :py:class:`ModelInfo <mlflow.models.model.ModelInfo>` instance that contains the
        model metadata.
        """
        return ModelInfo(
            artifact_path=self.artifact_path,
            flavors=self.flavors,
            model_uri="runs:/{}/{}".format(self.run_id, self.artifact_path),
            model_uuid=self.model_uuid,
            run_id=self.run_id,
            saved_input_example_info=self.saved_input_example_info,
            signature_dict=self.signature.to_dict() if self.signature else None,
            signature=self.signature,
            utc_time_created=self.utc_time_created,
            mlflow_version=self.mlflow_version,
        )

    def to_dict(self):
        """Serialize the model to a dictionary."""
        res = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        databricks_runtime = get_databricks_runtime()
        if databricks_runtime:
            res["databricks_runtime"] = databricks_runtime
        if self.signature is not None:
            res["signature"] = self.signature.to_dict()
        if self.saved_input_example_info is not None:
            res["saved_input_example_info"] = self.saved_input_example_info
        if self.mlflow_version is None and _MLFLOW_VERSION_KEY in res:
            res.pop(_MLFLOW_VERSION_KEY)
        return res

    def to_yaml(self, stream=None):
        """Write the model as yaml string."""
        return yaml.safe_dump(self.to_dict(), stream=stream, default_flow_style=False)

    def __str__(self):
        return self.to_yaml()

    def to_json(self):
        """Write the model as json."""
        return json.dumps(self.to_dict())

    def save(self, path):
        """Write the model as a local YAML file."""
        with open(path, "w") as out:
            self.to_yaml(out)

    @classmethod
    def load(cls, path):
        """Load a model from its YAML representation."""
        if os.path.isdir(path):
            path = os.path.join(path, MLMODEL_FILE_NAME)
        with open(path) as f:
            return cls.from_dict(yaml.safe_load(f.read()))

    @classmethod
    def from_dict(cls, model_dict):
        """Load a model from its YAML representation."""

        from .signature import ModelSignature

        model_dict = model_dict.copy()
        if "signature" in model_dict and isinstance(model_dict["signature"], dict):
            model_dict["signature"] = ModelSignature.from_dict(model_dict["signature"])

        if "model_uuid" not in model_dict:
            model_dict["model_uuid"] = None

        if _MLFLOW_VERSION_KEY not in model_dict:
            model_dict[_MLFLOW_VERSION_KEY] = None

        return cls(**model_dict)

    @classmethod
    def log(
        cls,
        artifact_path,
        flavor,
        registered_model_name=None,
        await_registration_for=DEFAULT_AWAIT_MAX_SLEEP_SECONDS,
        **kwargs,
    ):
        """
        Log model using supplied flavor module. If no run is active, this method will create a new
        active run.

        :param artifact_path: Run relative path identifying the model.
        :param flavor: Flavor module to save the model with. The module must have
                       the ``save_model`` function that will persist the model as a valid
                       MLflow model.
        :param registered_model_name: If given, create a model version under
                                      ``registered_model_name``, also creating a registered model if
                                      one with the given name does not exist.
        :param signature: :py:class:`ModelSignature` describes model input
                          and output :py:class:`Schema <mlflow.types.Schema>`. The model signature
                          can be :py:func:`inferred <infer_signature>` from datasets representing
                          valid model input (e.g. the training dataset) and valid model output
                          (e.g. model predictions generated on the training dataset), for example:

                          .. code-block:: python

                            from mlflow.models.signature import infer_signature
                            train = df.drop_column("target_label")
                            signature = infer_signature(train, model.predict(train))

        :param input_example: Input example provides one or several examples of
                              valid model input. The example can be used as a hint of what data to
                              feed the model. The given example will be converted to a Pandas
                              DataFrame and then serialized to json using the Pandas split-oriented
                              format. Bytes are base64-encoded.

        :param await_registration_for: Number of seconds to wait for the model version to finish
                            being created and is in ``READY`` status. By default, the function
                            waits for five minutes. Specify 0 or None to skip waiting.

        :param kwargs: Extra args passed to the model flavor.

        :return: A :py:class:`ModelInfo <mlflow.models.model.ModelInfo>` instance that contains the
                 metadata of the logged model.
        """
        with TempDir() as tmp:
            local_path = tmp.path("model")
            run_id = mlflow.tracking.fluent._get_or_start_run().info.run_id
            mlflow_model = cls(artifact_path=artifact_path, run_id=run_id)
            flavor.save_model(path=local_path, mlflow_model=mlflow_model, **kwargs)
            mlflow.tracking.fluent.log_artifacts(local_path, artifact_path)
            try:
                mlflow.tracking.fluent._record_logged_model(mlflow_model)
            except MlflowException:
                # We need to swallow all mlflow exceptions to maintain backwards compatibility with
                # older tracking servers. Only print out a warning for now.
                _logger.warning(_LOG_MODEL_METADATA_WARNING_TEMPLATE, mlflow.get_artifact_uri())
            if registered_model_name is not None:
                run_id = mlflow.tracking.fluent.active_run().info.run_id
                mlflow.register_model(
                    "runs:/%s/%s" % (run_id, artifact_path),
                    registered_model_name,
                    await_registration_for=await_registration_for,
                )
        return mlflow_model.get_model_info()


def get_model_info(model_uri: str) -> ModelInfo:
    """
    Create a :py:class:`ModelInfo <mlflow.models.model.ModelInfo>` instance that contains the
    model metadata from the logged model uri.

    :param model_uri: The location, in URI format, of the MLflow model. For example:

                      - ``/Users/me/path/to/local/model``
                      - ``relative/path/to/local/model``
                      - ``s3://my_bucket/path/to/model``
                      - ``runs:/<mlflow_run_id>/run-relative/path/to/model``
                      - ``models:/<model_name>/<model_version>``
                      - ``models:/<model_name>/<stage>``
                      - ``mlflow-artifacts:/path/to/model``

                      For more information about supported URI schemes, see
                      `Referencing Artifacts <https://www.mlflow.org/docs/latest/concepts.html#
                      artifact-locations>`_.

    :return: A :py:class:`ModelInfo <mlflow.models.model.ModelInfo>` instance that contains the
            metadata of the logged model.

    .. code-block:: python
            :caption: Example usage of get_model_info

            import mlflow.models
            import mlflow.sklearn
            from sklearn.ensemble import RandomForestRegressor

            with mlflow.start_run() as run:
                params = {"n_estimators": 3, "random_state": 42}
                X, y = [[0, 1]], [1]
                signature = mlflow.models.infer_signature(X, y)
                rfr = RandomForestRegressor(**params).fit(X, y)
                mlflow.log_params(params)
                mlflow.sklearn.log_model(rfr, artifact_path="sklearn-model", signature=signature)

            model_uri = "runs:/{}/sklearn-model".format(run.info.run_id)
            # Get model info with model_uri
            model_info = mlflow.models.get_model_info(model_uri)
            # Get model signature directly
            model_signature = model_info.signature
            assert model_signature == signature
    """
    from mlflow.pyfunc import _download_artifact_from_uri

    local_path = _download_artifact_from_uri(artifact_uri=model_uri, output_path=None)
    model_meta = Model.load(os.path.join(local_path, MLMODEL_FILE_NAME))
    return ModelInfo(
        artifact_path=model_meta.artifact_path,
        flavors=model_meta.flavors,
        model_uri=model_uri,
        model_uuid=model_meta.model_uuid,
        run_id=model_meta.run_id,
        saved_input_example_info=model_meta.saved_input_example_info,
        signature_dict=model_meta.signature.to_dict() if model_meta.signature else None,
        signature=model_meta.signature,
        utc_time_created=model_meta.utc_time_created,
        mlflow_version=model_meta.mlflow_version,
    )
