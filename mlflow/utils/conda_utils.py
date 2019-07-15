import hashlib
import json
import logging
import os
from mlflow.utils import process

from mlflow.exceptions import ExecutionException
# Environment variable indicating a path to a conda installation. MLflow will default to running
# "conda" if unset
MLFLOW_CONDA_HOME = "MLFLOW_CONDA_HOME"

_logger = logging.getLogger(__name__)


def _activate_conda_env_command(conda_env_name):
    activate_path = _get_conda_bin_executable("activate")
    return "source %s %s" % (activate_path, conda_env_name)


def _get_conda_bin_executable(executable_name):
    """
    Return path to the specified executable, assumed to be discoverable within the 'bin'
    subdirectory of a conda installation.

    The conda home directory (expected to contain a 'bin' subdirectory) is configurable via the
    ``mlflow.projects.MLFLOW_CONDA_HOME`` environment variable. If
    ``mlflow.projects.MLFLOW_CONDA_HOME`` is unspecified, this method simply returns the passed-in
    executable name.
    """
    conda_home = os.environ.get(MLFLOW_CONDA_HOME)
    if conda_home:
        return os.path.join(conda_home, "bin/%s" % executable_name)
    # Use CONDA_EXE as per https://github.com/conda/conda/issues/7126
    if "CONDA_EXE" in os.environ:
        conda_bin_dir = os.path.dirname(os.environ["CONDA_EXE"])
        return os.path.join(conda_bin_dir, executable_name)
    return executable_name


def _get_conda_env_name(conda_env_path, env_id=None):
    conda_env_contents = open(conda_env_path).read() if conda_env_path else ""
    if env_id:
        conda_env_contents += env_id
    return "mlflow-%s" % hashlib.sha1(conda_env_contents.encode("utf-8")).hexdigest()


def _get_or_create_conda_env(conda_env_path, env_id=None):
    """
    Given a `Project`, creates a conda environment containing the project's dependencies if such a
    conda environment doesn't already exist. Returns the name of the conda environment.
    :param conda_env_path: Path to a conda yaml file.
    :param env_id: Optional string that is added to the contents of the yaml file before
                   calculating the hash. It can be used to distinguish environments that have the
                   same conda dependencies but are supposed to be different based on the context.
                   For example, when serving the model we may install additional dependencies to the
                   environment after the environment has been activated.
    """
    conda_path = _get_conda_bin_executable("conda")
    try:
        process.exec_cmd([conda_path, "--help"], throw_on_error=False)
    except EnvironmentError:
        raise ExecutionException("Could not find Conda executable at {0}. "
                                 "Ensure Conda is installed as per the instructions "
                                 "at https://conda.io/docs/user-guide/install/index.html. You can "
                                 "also configure MLflow to look for a specific Conda executable "
                                 "by setting the {1} environment variable to the path of the Conda "
                                 "executable".format(conda_path, MLFLOW_CONDA_HOME))
    # The approach here is to directly run the user's conda executable (e.g. on Databricks or other
    # environments where MLFLOW_CONDA_HOME is set), and set up the shell to detect the conda
    # bash function otherwise
    (_, stdout, _) = process.exec_cmd([conda_path, "env", "list", "--json"])
    env_names = [os.path.basename(env) for env in json.loads(stdout)['envs']]
    project_env_name = _get_conda_env_name(conda_env_path, env_id)
    if project_env_name not in env_names:
        _logger.info('=== Creating conda environment %s ===', project_env_name)
        if conda_env_path:
            process.exec_cmd([conda_path, "env", "create", "-n", project_env_name, "--file",
                              conda_env_path], stream_output=True)
        else:
            process.exec_cmd([conda_path, "env", "create", "-n", project_env_name, "python"],
                             stream_output=True)
    return project_env_name
