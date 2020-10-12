from contextlib import contextmanager
import os
import tempfile

import matplotlib.pyplot as plt
import numpy as np
import shap

import mlflow

_SUMMARY_BAR_PLOT_FILE_NAME = "summary_bar_plot.png"
_BASE_VALUES_FILE_NAME = "base_values.npy"
_SHAP_VALUES_FILE_NAME = "shap_values.npy"


@contextmanager
def _log_artifact_contextmanager(out_file, artifact_path=None):
    """
    A context manager to make it easier to log an artifact.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = os.path.join(tmp_dir, out_file)
        yield tmp_path
        mlflow.log_artifact(tmp_path, artifact_path)


def _log_numpy(numpy_obj, out_file, artifact_path=None):
    """
    Log a numpy object.
    """
    with _log_artifact_contextmanager(out_file, artifact_path) as tmp_path:
        np.save(tmp_path, numpy_obj)


def _log_matplotlib_figure(fig, out_file, artifact_path=None):
    """
    Log a matplotlib figure.
    """
    with _log_artifact_contextmanager(out_file, artifact_path) as tmp_path:
        fig.savefig(tmp_path)


def log_explanation(predict_function, features, artifact_path=None):
    """
    Log a SHAP explanation.

    :param predict_function: A function to compute the output of a model.
    :param features: A matrix of features to compute SHAP values with.
    :param artifact_path: A run-relative artifact path the explanation is saved to.

    :return: A URI of the logged explanation.
    """
    artifact_path = "shap" if artifact_path is None else artifact_path
    explainer = shap.KernelExplainer(predict_function, shap.kmeans(features, 100))
    shap_values = explainer.shap_values(features)

    if isinstance(explainer.expected_value, list):
        base_values = np.array(explainer.expected_value)
        shap_values = np.array(shap_values)
    else:
        base_values = np.float(explainer.expected_value)

    _log_numpy(base_values, _BASE_VALUES_FILE_NAME, artifact_path)
    _log_numpy(shap_values, _SHAP_VALUES_FILE_NAME, artifact_path)

    shap.summary_plot(shap_values, features, plot_type="bar", show=False)
    fig = plt.gcf()
    _log_matplotlib_figure(fig, _SUMMARY_BAR_PLOT_FILE_NAME, artifact_path)
    plt.close(fig)
