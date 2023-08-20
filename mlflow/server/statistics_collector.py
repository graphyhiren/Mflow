import threading
import time

from prometheus_client import Gauge
from prometheus_client.metrics import MetricWrapperBase


class MLflowStatisticsCollector(threading.Thread):
    def __init__(
        self,
        update_interval_seconds,
        metrics_namespace="mlflow",
        metrics_multiprocess_mode="max",
    ):
        super().__init__(daemon=True)

        self.update_interval_seconds = update_interval_seconds
        self.metrics_config = {
            "namespace": metrics_namespace,
            "multiprocess_mode": metrics_multiprocess_mode,
        }
        self.default_labels = ("mlflow_version",)

        self._running_event = threading.Event()

    def register_metrics(self):
        self.user_count = Gauge(
            "user_count",
            "Total number of users",
            self.default_labels,
            **self.metrics_config,
        )

        self.experiment_count = Gauge(
            "experiment_count",
            "Total number of experiments",
            self.default_labels,
            **self.metrics_config,
        )

        self.run_count = Gauge(
            "run_count",
            "Total number of runs",
            self.default_labels,
            **self.metrics_config,
        )

        self.dataset_count = Gauge(
            "dataset_count",
            "Total number of datasets",
            self.default_labels,
            **self.metrics_config,
        )

        self.registered_model_count = Gauge(
            "registered_model_count",
            "Total number of registered models",
            self.default_labels + ("stage",),
            **self.metrics_config,
        )

        self.model_version_count = Gauge(
            "model_version_count",
            "Total number of model versions",
            self.default_labels + ("stage",),
            **self.metrics_config,
        )

    def get_registered_metrics(self):
        metrics = []
        for attribute_name in dir(self):
            attribute_value = getattr(self, attribute_name)
            if isinstance(attribute_value, MetricWrapperBase):
                metrics.append(attribute_value)
        return metrics

    def collect_metrics(self):
        """
        TODO(impl, tests, docs): collect metrics, add tests and documentation.
        Use `_get_tracking_store()` and others to collect counts.
        1) Introduce count method to stores or,
        2) Use existing search methods (non-optimized)
        """
        pass

    def run(self):
        self._running_event.set()
        while self._running_event.is_set():
            self.collect_metrics()
            time.sleep(self.update_interval_seconds)

    def stop(self):
        self._running_event.clear()


__all__ = ["MLflowStatisticsCollector"]
