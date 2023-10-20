"""System metrics logging module."""

from mlflow.environment_variables import (
    MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING,
    MLFLOW_SYSTEM_METRICS_SAMPLES_BEFORE_LOGGING,
    MLFLOW_SYSTEM_METRICS_SAMPLING_INTERVAL,
)
from mlflow.utils.annotations import experimental


@experimental
def disable_system_metrics_logging():
    """Disable system metrics logging globally.

    Calling this function will disable system metrics logging globally, but users can still opt in
    system metrics logging for individual runs by `mlflow.start_run(log_system_metrics=True)`.
    """
    MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING.set(False)


@experimental
def enable_system_metrics_logging():
    """Enable system metrics logging globally.

    Calling this function will enable system metrics logging globally, but users can still opt out
    system metrics logging for individual runs by `mlflow.start_run(log_system_metrics=False)`.
    """
    MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING.set(True)


@experimental
def set_system_metrics_sampling_interval(interval):
    """Set the system metrics sampling interval.

    Every `interval` seconds, the system metrics will be collected. By default `interval=10`.
    """
    if interval is None:
        MLFLOW_SYSTEM_METRICS_SAMPLING_INTERVAL.unset()
    else:
        MLFLOW_SYSTEM_METRICS_SAMPLING_INTERVAL.set(interval)


@experimental
def set_system_metrics_samples_before_logging(samples):
    """Set the number of samples before logging system metrics.

    Every time `samples` samples have been collected, the system metrics will be logged to mlflow.
    By default `samples=1`.
    """
    if samples is None:
        MLFLOW_SYSTEM_METRICS_SAMPLES_BEFORE_LOGGING.unset()
    else:
        MLFLOW_SYSTEM_METRICS_SAMPLES_BEFORE_LOGGING.set(samples)
