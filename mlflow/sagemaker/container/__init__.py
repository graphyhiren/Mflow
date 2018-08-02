"""
Initialize the environment and start model serving on Sagemaker or local Docker container.

To be executed only during the model deployment.

"""
from __future__ import print_function

import multiprocessing
import os
import shutil
import signal
from subprocess import check_call, Popen
import sys

from pkg_resources import resource_filename

import mlflow
import mlflow.version

from mlflow import pyfunc
from mlflow.models import Model
from mlflow.version import VERSION as MLFLOW_VERSION

# Supported versions are listed at https://conda.io/docs/user-guide/tasks/manage-python.html
SUPPORTED_CONDA_PY_VERSIONS = ['2.7', '3.4', '3.5', '3.6']

def _init(cmd):
    """
    Initialize the container and execute command.

    :param cmd: Command param passed by Sagemaker. Can be  "serve" or "train" (unimplemented).
    """
    if cmd == 'serve':
        _serve()
    elif cmd == 'train':
        _train()
    else:
        raise Exception("Unrecognized command {cmd}, full args = {args}".format(cmd=cmd,
                                                                                args=str(sys.argv)))


def _server_dependencies_cmds():
    """
    Get commands required to install packages required to serve the model with MLflow. These are
    packages outside of the user-provided environment, except for the MLflow itself.

    :return: List of commands.
    """
    # TODO: Should we reinstall MLflow? What if there is MLflow in the user's conda environment?
    return ["conda install -c anaconda gunicorn", "conda install -c anaconda gevent",
            "pip install /opt/mlflow/." if os.path.isdir("/opt/mlflow")
            else "pip install mlflow=={}".format(MLFLOW_VERSION)]


def _serve():
    """
    Serve the model.

    Read the MLmodel config, initialize the Conda environment if needed and start python server.
    """
    m = Model.load("/opt/ml/model/MLmodel")
    if pyfunc.FLAVOR_NAME not in m.flavors:
        raise Exception("Only supports pyfunc models and this is not one.")
    conf = m.flavors[pyfunc.FLAVOR_NAME]
    bash_cmds = []
    if pyfunc.ENV in conf:
        _print_flush("activating custom Anaconda environment")
        env = conf[pyfunc.ENV]
        env_path_dst = os.path.join("/opt/mlflow/", env)
        env_path_dst_dir = os.path.dirname(env_path_dst)
        if not os.path.exists(env_path_dst_dir):
            os.makedirs(env_path_dst_dir)
        # TODO: should we test that the environment does not include any of the server dependencies?
        # Those are gonna be reinstalled. should probably test this on the client side
        shutil.copyfile(os.path.join("/opt/ml/model/", env), env_path_dst)
        env_name = "custom_env"
        os.system("conda env create -n {en} -f {ep}".format(en=env_name, ep=env_path_dst))
        bash_cmds += ["source /miniconda/bin/activate custom_env"] + _server_dependencies_cmds()
    elif pyfunc.PY_VERSION in conf:
        model_py_version = conf[pyfunc.PY_VERSION]
        if model_py_version in SUPPORTED_CONDA_PY_VERSIONS:
            env_name = "py_env"
            _print_flush("activating default environment for Python version {mpyv}".format(
                mpyv=model_py_version))
            os.system("conda create -n {en} python={mpyv} anaconda".format(en=env_name, 
                                                                           mpyv=model_py_version))
            bash_cmds += ["source /miniconda/bin/activate {en}".format(en=env_name)] + \
                    _server_dependencies_cmds()
        else:
            _print_flush("The version of python used to serialize the model: Python {mpyv} is not" 
                         " supported by Anaconda.".format(mpyv=model_py_version))
    else:
        default_python_version = "{vmaj}.{vmin}".format(vmaj=sys.version_info.major,
                                                        vmin=sys.version_info.minor)
        _print_flush("Using the default Anaconda environment with Python {dpyv}, which may not be" 
                     " compatible with the model.".format(dpyv=default_python_version))

    nginx_conf = resource_filename(mlflow.sagemaker.__name__, "container/scoring_server/nginx.conf")
    nginx = Popen(['nginx', '-c', nginx_conf])
    # link the log streams to stdout/err so they will be logged to the container logs
    check_call(['ln', '-sf', '/dev/stdout', '/var/log/nginx/access.log'])
    check_call(['ln', '-sf', '/dev/stderr', '/var/log/nginx/error.log'])
    cpu_count = multiprocessing.cpu_count()
    os.system("pip -V")
    os.system("python -V")
    os.system('python -c"from mlflow.version import VERSION as V; print(V)"')
    cmd = ("gunicorn --timeout 60 -k gevent -b unix:/tmp/gunicorn.sock -w {nworkers} " +
           "mlflow.sagemaker.container.scoring_server.wsgi:app").format(nworkers=cpu_count)
    bash_cmds.append(cmd)
    gunicorn = Popen(["/bin/bash", "-c", "; ".join(bash_cmds)])
    signal.signal(signal.SIGTERM, lambda a, b: _sigterm_handler(nginx.pid, gunicorn.pid))
    # If either subprocess exits, so do we.
    pids = set([nginx.pid, gunicorn.pid])
    while True:
        pid, _ = os.wait()
        if pid in pids:
            break
    _sigterm_handler(nginx.pid, gunicorn.pid)


def _train():
    raise Exception("Train is not implemented.")


def _print_flush(content):
    print(content)
    sys.stdout.flush()


def _sigterm_handler(nginx_pid, gunicorn_pid):
    """
    Cleanup when terminating.

    Attempt to kill all launched processes and exit.

    """
    print("Got sigterm signal, exiting.")
    try:
        os.kill(nginx_pid, signal.SIGQUIT)
    except OSError:
        pass
    try:
        os.kill(gunicorn_pid, signal.SIGTERM)
    except OSError:
        pass

    sys.exit(0)
