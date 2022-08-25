import os

import mlflow
from mlflow.tracking.artifact_utils import _download_artifact_from_uri
from mlflow.pyfunc.model import Model, MLMODEL_FILE_NAME
from mlflow.store.artifact.utils.models import _parse_model_uri
from mlflow.utils.environment import (
    _REQUIREMENTS_FILE_NAME,
)
from mlflow.exceptions import MlflowException
from mlflow.protos.databricks_pb2 import BAD_REQUEST
from mlflow.utils.environment import _mlflow_conda_env
from mlflow.utils.model_utils import _validate_and_prepare_target_save_path

_WHEELS_FOLDER_NAME = "wheels"


class WheeledModel:
    def __init__(self, model_uri):
        self._model_uri = model_uri
        self._model_name, _, _ = _parse_model_uri(model_uri)  # Throws exception if not a model uri

    @classmethod
    def log_model(cls, artifact_path, model_uri, **kwargs):
        model_name, _, _ = _parse_model_uri(model_uri)
        return Model.log(
            artifact_path=artifact_path,
            flavor=WheeledModel(model_uri),
            registered_model_name=kwargs.pop("registered_model_name", model_name),
            **kwargs,
        )

    def save_model(self, path, mlflow_model=None):
        from mlflow.pyfunc import FLAVOR_NAME, ENV

        path = os.path.abspath(path)
        _validate_and_prepare_target_save_path(path)

        local_model_path = _download_artifact_from_uri(self._model_uri, output_path=path)

        wheels_dir = os.path.join(local_model_path, _WHEELS_FOLDER_NAME)
        pip_requirements_path = os.path.join(local_model_path, _REQUIREMENTS_FILE_NAME)
        model_metadata_path = os.path.join(local_model_path, MLMODEL_FILE_NAME)

        model_metadata = Model.load(model_metadata_path)

        # Check if the model file has `wheels` set to True
        if model_metadata.__dict__.get(_WHEELS_FOLDER_NAME, None):
            raise MlflowException("Cannot add wheels to a wheeled model", BAD_REQUEST)

        conda_env = model_metadata.flavors.get(FLAVOR_NAME, {}).get(ENV, None)
        conda_env_path = os.path.join(local_model_path, conda_env)
        if conda_env is None:
            raise MlflowException(
                "Can not add wheels for model with no conda environment.", BAD_REQUEST
            )
        if not os.path.isfile(pip_requirements_path):
            raise Exception("Can not add wheels for model with no 'requirements.txt'.")

        self._download_wheels(dst_path=wheels_dir, pip_requirements_path=pip_requirements_path)

        # Update requirements.txt with wheels
        pip_wheels = self._overwrite_pip_requirements_with_wheels(
            wheels_dir=wheels_dir, pip_requirements_path=pip_requirements_path
        )

        _mlflow_conda_env(path=conda_env_path, additional_pip_deps=pip_wheels, install_mlflow=False)

        # Update MLModel File
        mlflow_model = self._update_mlflow_model(
            mlflow_model=mlflow_model, original_model_metadata=model_metadata
        )
        mlflow_model.save(model_metadata_path)
        return mlflow_model

    def _update_mlflow_model(self, mlflow_model, original_model_metadata):
        """
        Updates the MLModel file with the correct run_id, and utc_time_created. Additionally,
        this also adds `wheels` to the list of artifacts.
        :param mlflow_model: :py:mod:`mlflow.models.Model` configuration to which to add the
                             **python_function** flavor.
        :param original_model_file_path: Path to the original model file
        """

        run_id = mlflow.tracking.fluent._get_or_start_run().info.run_id
        if mlflow_model is None:
            mlflow_model = Model(run_id=run_id)

        original_model_metadata.__dict__.update(
            {k: v for k, v in mlflow_model.__dict__.items() if v}
        )
        mlflow_model.__dict__.update(original_model_metadata.__dict__)

        mlflow_model.wheels = _WHEELS_FOLDER_NAME
        return mlflow_model

    def _download_wheels(self, dst_path, pip_requirements_path):
        """
        Downloads all the wheels of the dependencies specified in the requirements.txt file
        :param dst_path: Path to the directory where the wheels are to be downloaded
        :param pip_requirements_path: Path to requirements.txt in the model directory
        """
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)

        download_command = (
            f"python -m pip wheel --only-binary=:all: --wheel-dir={dst_path} -r"
            f"{pip_requirements_path} --no-cache-dir"
        )
        rc = os.system(download_command)
        if rc != 0:
            raise MlflowException("Error downloading dependency wheels")

    def _overwrite_pip_requirements_with_wheels(self, wheels_dir, pip_requirements_path):
        """
        Overwrites the requirements.txt with the wheels of the required dependencies.
        :param wheels_dir: Path to directory where wheels are stored
        :param pip_requirements_path: Path to requirements.txt in the model directory
        """
        wheels = []
        with open(pip_requirements_path, "w") as wheels_requirements:
            for wheel_file in os.listdir(wheels_dir):
                if wheel_file.endswith(".whl"):
                    complete_wheel_file = os.path.join(_WHEELS_FOLDER_NAME, wheel_file)
                    wheels.append(complete_wheel_file)
                    wheels_requirements.write(complete_wheel_file + "\n")
        return wheels
