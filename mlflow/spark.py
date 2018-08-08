"""
MLflow integration for Spark MLlib models.

This module enables the exporting of Spark MLlib models with the following flavors (formats):
    1. Spark MLLib (native) format - Allows models to be loaded as Spark Transformers for scoring
                                     in a Spark session.
    2. PyFunc - Supports deployment outside of Spark by instantiating a SparkContext and reading 
                input data as a Spark DataFrame prior to scoring.
    3. MLeap - Enables high-performance deployment outside of Spark by leveraging MLeap's
               custom dataframe and pipeline representations. For more informatin about MLeap,
               see https://github.com/combust/mleap.
"""

from __future__ import absolute_import


import os


import mlflow
from mlflow import pyfunc, mleap, sparkml
from mlflow.models import Model
from mlflow.utils.environment import add_conda_env 
from mlflow.utils.exception import SaveModelException 
from mlflow.utils.logging_utils import eprint 


LEGACY_FLAVOR_NAME = "spark"


def log_model(spark_model, artifact_path, conda_env=None, jars=None, dfs_tmpdir=sparkml.DFS_TMP, 
              sample_input=None):
    """
    Log a Spark MLlib model as an MLflow artifact for the current run.

    :param spark_model: PipelineModel to be saved.
    :param artifact_path: Run-relative artifact path.
    :param conda_env: Path to a Conda environment file. If provided, this defines enrionment for
           the model. At minimum, it should specify python, pyspark and mlflow with appropriate
           versions.
    :param jars: List of jars needed by the model.
    :param dfs_tmpdir: Temporary directory path on Distributed (Hadoop) File System (DFS) or local
        filesystem if running in local mode. The model will be written to this destination and then 
        copied into the model's artifact directory. This is necessary because Spark ML models
        read from / write to DFS if running on a cluster. All temporary files created on the
        DFS will be removed if this operation completes successfully.
    :param sample_input: A sample input that the model can evaluate. This is required in order to
                         add the MLeap flavor to the model. If `sample_input` is `None`, the MLeap
                         flavor will not be added.
    """
    return Model.log(artifact_path=artifact_path, flavor=mlflow.spark, spark_model=spark_model,
                     jars=jars, conda_env=conda_env, dfs_tmpdir=dfs_tmpdir, 
                     sample_input=sample_input)


def save_model(spark_model, path, mlflow_model=Model(), conda_env=None, jars=None, 
        dfs_tmpdir=sparkml.DFS_TMP, sample_input=None):
    """
    Save Spark MLlib PipelineModel at given local path.

    Uses Spark MLLib (sparkml) and MLeap mechanisms. The MLeap flavor will only
    be added if the PipelineModel is MLeap-compatible and a sample input is provided. 

    :param spark_model: Spark PipelineModel to be saved. Can save only PipelineModels.
    :param path: Local path where the model is to be saved.
    :param mlflow_model: MLflow model config this flavor is being added to.
    :param conda_env: Path to a Conda environment file. If provided, defines environment for the
        model. At minimum, it should specify python, pyspark, and mlflow with appropriate versions.
    :param jars: List of jars needed by the model.
    :param dfs_tmpdir: Temporary directory path on Distributed (Hadoop) File System (DFS) or local
        filesystem if running in local mode. The model will be written to this destination and then 
        copied into the model's artifact directory. This is necessary because Spark ML models
        read from / write to DFS if running on a cluster. All temporary files created on the
        DFS will be removed if this operation completes successfully.
    :param sample_input: A sample input that the model can evaluate. This is required in order to
                         add the MLeap flavor to the model. If `sample_input` is `None`, the MLeap
                         flavor will not be added.
    """
    if jars:
        raise SaveModelException("jar dependencies are not implemented")
    
    try:
        mleap.add_to_model(mlflow_model, path, spark_model, sample_input)
        print("Added the MLeap flavor to the model.")
    except SaveModelException as e:
        eprint("An error occurred while adding the MLeap flavor to the model!" 
               " Error text: {err}".format(err=e))

    try:
        sparkml.add_to_model(mlflow_model, path, spark_model, dfs_tmpdir)
        print("Added the SparkML flavor to the model.")
        model_conda_env = add_conda_env(path, conda_env)
        pyfunc.add_to_model(mlflow_model, loader_module="mlflow.spark", data="model",
                            env=model_conda_env)
        print("Added the PyFunc flavor to the model.")
    except SaveModelException as e:
        eprint("An error occurred while adding the SparkML flavor to the model! Because"
               " the SparkML flavor could not be added, the PyFunc flavor will also be"
               " omitted. Error text: {err}".format(err=e))

    if len(mlflow_model.flavors) > 0:
        mlflow_model.save(os.path.join(path, "MLmodel"))
    else:
        raise SaveModelException("Failed to save the model because no supported flavors could be"
                                 " added. See preceding error logs for details!")


def load_model(path, run_id=None, dfs_tmpdir=sparkml.DFS_TMP):
    """
    Load the Spark MLlib model from the path.

    :param run_id: Run ID. If provided, combined with ``path`` to identify the model.
    :param path: Local filesystem path or run-relative artifact path to the model.
    :param dfs_tmpdir: Temporary directory path on Distributed (Hadoop) File System (DFS) or local
        filesystem if running in local mode. The model will be read from this path and then 
        copied into the model's artifact directory. This is necessary because Spark ML models
        read from / write to / DFS if running on a cluster. All temporary files created on the
        DFS will be removed if this operation completes successfully.
    :return: SparkML model.
    :rtype: pyspark.ml.pipeline.PipelineModel
    """
    if run_id is not None:
        path = mlflow.tracking._get_model_log_dir(model_name=path, run_id=run_id)
    m = Model.load(os.path.join(path, 'MLmodel'))
    supported_flavors = [flav for flav in m.flavors if flav in 
            [LEGACY_FLAVOR_NAME, sparkml.FLAVOR_NAME]]
    if len(supported_flavors) == 0:
        raise Exception("Model does not have {flav_sparkml} flavor or legacy {flav_spark} flavor.".
                format(flav_sparkml=sparkml.FLAVOR_NAME, flav_spark=LEGACY_FLAVOR_NAME))
    flavor = supported_flavors[0]
    conf = m.flavors[flavor]
    return sparkml.load_model(flavor, conf, dfs_tmpdir)


def load_pyfunc(path):
    """
    Load a Python Function model from a local file.

    :param path: Local path.
    :return: The model as PyFunc.
    """
    return sparkml.load_pyfunc(path)
