from __future__ import absolute_import

import click
import os
import subprocess
import sys

from mlflow.tracking import _get_model_log_dir
from mlflow.utils import cli_args
from mlflow.utils.logging_utils import eprint

@click.group("rfunc")
def commands():
    """Serve R models locally."""
    pass

def execute(command):
    eprint("=== Rscript -e %s) ===" % command)
    env = os.environ.copy()
    process = subprocess.Popen(["Rscript", "-e", command], close_fds=True, env=env)
    process.wait()

@commands.command("serve")
@cli_args.MODEL_PATH
@cli_args.RUN_ID
@click.option("--port", "-p", default=5000, help="Server port. [default: 5000]")
def serve(model_path, run_id, port):
    """
    Serve an RFunction model saved with MLflow.

    If a ``run_id`` is specified, ``model-path`` is treated as an artifact path within that run;
    otherwise it is treated as a local path.
    """
    if run_id:
        model_path = _get_model_log_dir(model_path, run_id)
    
    command = "mlflow::mlflow_serve('{0}', port = {1})".format(model_path, port)
    execute(command)

@commands.command("predict")
@cli_args.MODEL_PATH
@cli_args.RUN_ID
@click.option("--input-path", "-i", help="JSON containing DataFrame to predict against.",
              required=True)
@click.option("--output-path", "-o", help="File to output results to as JSON file." +
                                          " If not provided, output to stdout.")
def predict(model_path, run_id, input_path, output_path):
    """
    Serve an RFunction model saved with MLflow.
    Return the prediction results as a JSON DataFrame.

    If a ``run-id`` is specified, ``model-path`` is treated as an artifact path within that run;
    otherwise it is treated as a local path.
    """
    if run_id:
        model_path = _get_model_log_dir(model_path, run_id)

    command = "mlflow::mlflow_predict('{0}', '{1}', '{2}')".format(model_path, input_path, output_path)
    execute(command)
