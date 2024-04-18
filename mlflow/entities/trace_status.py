from enum import Enum

from opentelemetry import trace as trace_api

from mlflow.protos.service_pb2 import TraceStatus as ProtoTraceStatus


class TraceStatus(str, Enum):
    """Enum for status of an :py:class:`mlflow.entities.TraceInfo`."""

    UNSPECIFIED = "TRACE_STATUS_UNSPECIFIED"
    OK = "OK"
    ERROR = "ERROR"
    IN_PROGRESS = "IN_PROGRESS"

    def to_proto(self):
        return ProtoTraceStatus.Value(self)

    @staticmethod
    def from_proto(proto_status):
        return ProtoTraceStatus.Name(proto_status)

    def to_otel_status(self) -> trace_api.Status:
        return trace_api.Status(_MLFLOW_STATUS_CODE_TO_OTEL[self])

    @staticmethod
    def from_otel_status(otel_status: trace_api.Status):
        return _OTEL_STATUS_CODE_TO_MLFLOW[otel_status.status_code]


_OTEL_STATUS_CODE_TO_MLFLOW = {
    trace_api.StatusCode.OK: TraceStatus.OK,
    trace_api.StatusCode.ERROR: TraceStatus.ERROR,
    trace_api.StatusCode.UNSET: TraceStatus.UNSPECIFIED,
}

_MLFLOW_STATUS_CODE_TO_OTEL = {value: key for key, value in _OTEL_STATUS_CODE_TO_MLFLOW.items()}
