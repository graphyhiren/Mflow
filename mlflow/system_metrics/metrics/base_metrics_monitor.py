"""Base class of system metrics monitor."""
import abc
from collections import defaultdict


class BaseMetricsMonitor(abc.ABC):
    """Base class of system metrics monitor.

    Args:
        name: string, name of the monitor.
    """

    def __init__(self, name):
        self.name = name

        self._metrics = defaultdict(list)

    @abc.abstractmethod
    def collect_metrics(self):
        raise NotImplementedError

    def aggregate_metrics(self):
        metrics = {}
        for name, values in self._metrics.items():
            if len(values) > 0:
                metrics[name] = sum(values) / len(values)
        return metrics

    @property
    def metrics(self):
        return self._metrics

    def clear_metrics(self):
        self._metrics.clear()
