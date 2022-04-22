from mlflow.entities._mlflow_object import _MLflowObject
from mlflow.protos.service_pb2 import Param as ProtoParam

from .conversion_utils import convert_to_str_if_possible

class Param(_MLflowObject):
    """
    Parameter object.
    """

    def __init__(self, key, value):
        key = convert_to_str_if_possible(key)
        value = convert_to_str_if_possible(value)

        self._key = key
        self._value = value

    @property
    def key(self):
        """String key corresponding to the parameter name."""
        return self._key

    @property
    def value(self):
        """String value of the parameter."""
        return self._value

    def to_proto(self):
        param = ProtoParam()
        param.key = self.key
        param.value = self.value
        return param

    @classmethod
    def from_proto(cls, proto):
        return cls(proto.key, proto.value)

    def __eq__(self, __o):
        if isinstance(__o, self.__class__):
            return self._key == __o._key

        return False

    def __hash__(self):
        return hash(self._key)
