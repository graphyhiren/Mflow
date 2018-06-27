"""
MLflow integration for SparkML models.

SparkML models are saved and loaded using native SparkML persistence.
The models can be exported as pyfunc for out-of Spark deployment or it can be loaded back as Spark
Transformer in order to score it in Spark. The pyfunc flavor instantiates SparkContext internally
and reads the input data as Spark DataFrame prior to scoring.
"""

from __future__ import absolute_import

import os
import shutil

import pyspark
from pyspark.ml.pipeline import PipelineModel
from pyspark.ml.base import Transformer


import mlflow
from mlflow import pyfunc
from mlflow.models import Model


FLAVOR_NAME = "sparkml"


def log_model(spark_model, artifact_path, conda_env=None, jars=None):
    """
    Log a Spark MLlib model as an MLflow artifact for the current run.

    :param spark_model: PipelineModel to be saved.
    :param artifact_path: Run-relative artifact path.
    :param conda_env: Path to a Conda environment file. If provided, this defines enrionment for
           the model. At minimum, it should specify python, pyspark and mlflow with appropriate
           versions.
    :param jars: List of jars needed by the model.
    """
    return Model.log(artifact_path=artifact_path, flavor=mlflow.sparkml, spark_model=spark_model,
                     jars=jars, env=conda_env)


def save_model(spark_model, path, mlflow_model=Model(), conda_env=None, jars=None):
    """
    Save Spark MLlib PipelineModel at given local path.

    Uses Spark MLlib persistence mechanism.

    :param spark_model: Spark PipelineModel to be saved. Currently can only save PipelineModels.
    :param path: Local path where the model is to be saved.
    :param mlflow_model: MLflow model config this flavor is being added to.
    :param conda_env: Conda environment this model depends on.
    :param jars: List of jars needed by the model.
    """
    if jars:
        raise Exception("jar dependencies are not implemented")
    if not isinstance(spark_model, Transformer):
        raise Exception("Unexpected type {}. SparkML model works only with Transformers".format(
            str(type(spark_model))))
    if not isinstance(spark_model, PipelineModel):
        raise Exception("Not a PipelineModel. SparkML can currently only save PipelineModels.")
    spark_model.save(os.path.join(path, "model"))
    pyspark_version = pyspark.version.__version__
    model_conda_env = None
    if conda_env:
        model_conda_env = os.path.basename(os.path.abspath(conda_env))
        shutil.copyfile(conda_env, os.path.join(path, model_conda_env))
    if jars:
        raise Exception("jar dependencies are not yet implemented")
    mlflow_model.add_flavor('sparkml', pyspark_version=pyspark_version, model_data="model")
    pyfunc.add_to_model(mlflow_model, loader_module="mlflow.sparkml", data="model",
                        env=model_conda_env)
    mlflow_model.save(os.path.join(path, "MLmodel"))


def load_model(path, run_id=None):
    """
    Load the Spark MLlib model from the given path.
    :param run_id: Run ID. If provided it is combined with path to identify the model.
    :param path: Local filesystem path or Run-relative artifact path to the model.
    :return: SparkML model.
    :rtype: pyspark.ml.pipeline.PipelineModel
    """
    if run_id is not None:
        path = mlflow.tracking._get_model_log_dir(model_name=path, run_id=run_id)
    m = Model.load(path)
    if FLAVOR_NAME not in m.flavors:
        raise Exception("Model does not have {} flavor".format(FLAVOR_NAME))
    conf = m.flavors[FLAVOR_NAME]
    return PipelineModel.load(conf['model_data'])


def load_pyfunc(path):
    """
    Load the model as PyFunc.
    :param path: Local path
    :return: The model as PyFunc.
    """
    spark = pyspark.sql.SparkSession.builder.config(key="spark.python.worker.reuse", value=True) \
        .master("local[1]").getOrCreate()
    return _PyFuncModelWrapper(spark, PipelineModel.load(path))


class _PyFuncModelWrapper(object):
    """
    Wrapper around Spark MLlib PipelineModel providing interface for scoring pandas DataFrame.
    """
    def __init__(self, spark, spark_model):
        self.spark = spark
        self.spark_model = spark_model

    def predict(self, pandas_df):
        """
        Generate predictions given input data in Pandas DataFrame.

        :param pandas_df:
        :return: list with model predictions
        :rtype: list
        """
        spark_df = self.spark.createDataFrame(pandas_df)
        return [x.prediction for x in
                self.spark_model.transform(spark_df).select("prediction").collect()]
