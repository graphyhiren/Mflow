"""
CLI for azureml module.
"""
from __future__ import print_function

import json

import click

from mlflow.utils import cli_args


@click.group("azureml")
def commands():
    """
    Serve models on Azure ML.

    To serve a model associated with a run on a tracking server, set the MLFLOW_TRACKING_URI
    environment variable to the URL of the desired server.
    """
    pass


@commands.command("build-image")
@cli_args.MODEL_PATH
@click.option("--workspace-name", "-w", required=True,
              help="The name of the Azure Workspace in which to build the image.")
@click.option("--subscription-id", "-s", default=None,
              help=("The subscription id associated with the Azure Workspace in which to build"
                    " the image"))
@cli_args.RUN_ID
@click.option("--image-name", "-i", default=None,
              help=("The name to assign the Azure Container Image that is created. If unspecified,"
                    " a unique image name will be generated."))
@click.option("--model-name", "-n", default=None,
              help=("The name to assign the Azure Model that is created. If unspecified,"
                    " a unique image name will be generated."))
@cli_args.MLFLOW_HOME
@click.option("--description", "-d", default=None,
              help=("A string description to associate with the Azure Container Image and the"
                    " Azure Model that are created."))
@click.option("--tags", "-t", default=None,
              help=("A collection of tags, represented as a JSON-formatted dictionary of string"
                    " key-value pairs, to associate with the Azure Container Image and the Azure"
                    " Model that are created. These tags will be added to a set of default tags"
                    " that include the model path, the model run id (if specified), and more."))
def build_image(model_path, workspace_name, subscription_id, run_id, image_name, model_name,
                mlflow_home, description, tags):
    """
    Register an MLflow model with Azure ML and build an Azure ML ContainerImage for deployment.
    The resulting image can be deployed as a web service to Azure Container Instances (ACI) or
    Azure Kubernetes Service (AKS).
    """
    # If users do not have the Azure ML SDK installed, they should still be able to view the
    # usage guide for the command associated with this method. Therefore, we do not attempt to
    # import modules dependent on the SDK until this method is invoked.
    import mlflow.azureml
    from azureml.core import Workspace

    workspace = Workspace.get(name=workspace_name, subscription_id=subscription_id)
    if tags is not None:
        tags = json.loads(tags)
    mlflow.azureml.build_image(
            model_path=model_path, workspace=workspace, run_id=run_id, image_name=image_name,
            model_name=model_name,  mlflow_home=mlflow_home, description=description, tags=tags,
            synchronous=True)
