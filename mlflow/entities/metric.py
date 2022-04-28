from mlflow.entities._mlflow_object import _MLflowObject
from mlflow.protos.service_pb2 import Metric as ProtoMetric

from .metic_value_conversion_utils import (
    convert_metric_value_to_float_if_possible,
    convert_metric_value_to_str_if_possible,
)


class Metric(_MLflowObject):
    """
    Metric object.

    Args:
        key: `str`, `pyspark.ml.param.Param`, `numpy.ndarray`, `tensorflow.Tensor` or `torch.Tensor`

        Multidimensional arrays or tensors will be stringified after being converted to a list.

        value: `float`, `numpy.ndarray`, `tensorflow.Tensor` or `torch.Tensor`

        Multidimensional arrays or tensors should contain a single element in order for them
        to be converted to a float value.

    """

    def __init__(self, key, value, timestamp, step):
        self._key = convert_metric_value_to_str_if_possible(key)

        self._value = convert_metric_value_to_float_if_possible(value, convert_int=False)

        self._timestamp = timestamp
        self._step = step

    @property
    def key(self):
        """String key corresponding to the metric name."""
        return self._key

    @property
    def value(self):
        """Float value of the metric."""
        return self._value

    @property
    def timestamp(self):
        """Metric timestamp as an integer (milliseconds since the Unix epoch)."""
        return self._timestamp

    @property
    def step(self):
        """Integer metric step (x-coordinate)."""
        return self._step

    def to_proto(self):
        metric = ProtoMetric()
        metric.key = self.key
        metric.value = self.value
        metric.timestamp = self.timestamp
        metric.step = self.step
        return metric

    @classmethod
    def from_proto(cls, proto):
        return cls(proto.key, proto.value, proto.timestamp, proto.step)

    def __eq__(self, __o):
        if isinstance(__o, self.__class__):
            return self.__dict__ == __o.__dict__

        return False

    def __hash__(self):
        return hash((self._key, self._value, self._timestamp, self._step))
