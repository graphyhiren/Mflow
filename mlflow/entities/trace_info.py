from dataclasses import dataclass
from typing import List, Optional

from mlflow.entities._mlflow_object import _MLflowObject
from mlflow.entities.trace_request_metadata import TraceRequestMetadata
from mlflow.entities.trace_status import TraceStatus
from mlflow.entities.trace_tag import TraceTag
from mlflow.protos.service_pb2 import TraceInfo as ProtoTraceInfo


@dataclass
class TraceInfo(_MLflowObject):
    """Metadata about a trace.

    Args:
        request_id: id of the trace.
        experiment_id: id of the experiment.
        timestamp_ms: start time of the trace, in milliseconds.
        execution_time_ms: duration of the trace, in milliseconds.
        status: status of the trace.
        request_metadata: request metadata associated with the trace.
        tags: tags associated with the trace.
    """

    request_id: str
    experiment_id: str
    timestamp_ms: int
    execution_time_ms: Optional[int]
    status: TraceStatus
    request_metadata: Optional[List[TraceRequestMetadata]] = None
    tags: Optional[List[TraceTag]] = None

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def to_proto(self):
        proto = ProtoTraceInfo()
        proto.request_id = self.request_id
        proto.experiment_id = self.experiment_id
        proto.timestamp_ms = self.timestamp_ms
        proto.execution_time_ms = self.execution_time_ms
        proto.status = TraceStatus.from_string(self.status)
        proto.request_metadata.extend([attr.to_proto() for attr in self.request_metadata])
        proto.tags.extend([tag.to_proto() for tag in self.tags])
        return proto

    @classmethod
    def from_proto(cls, proto):
        return cls(
            request_id=proto.request_id,
            experiment_id=proto.experiment_id,
            timestamp_ms=proto.timestamp_ms,
            execution_time_ms=proto.execution_time_ms,
            status=TraceStatus.to_string(proto.status),
            request_metadata=[
                TraceRequestMetadata.from_proto(attr) for attr in proto.request_metadata
            ],
            tags=[TraceTag.from_proto(tag) for tag in proto.tags],
        )
