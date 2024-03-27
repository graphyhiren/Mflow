import time
from unittest import mock

import mlflow
from mlflow.entities.span import SpanType
from mlflow.entities.trace_status import TraceStatus
from mlflow.tracing.types.constant import TraceMetadataKey


def test_trace(mock_client):
    class TestModel:
        @mlflow.trace()
        def predict(self, x, y):
            z = x + y
            z = self.add_one(z)
            z = mlflow.trace(self.square)(z)
            return z  # noqa: RET504

        @mlflow.trace(
            span_type=SpanType.LLM, name="add_one_with_custom_name", attributes={"delta": 1}
        )
        def add_one(self, z):
            return z + 1

        def square(self, t):
            res = t**2
            time.sleep(0.1)
            return res

    model = TestModel()
    model.predict(2, 5)

    trace = mlflow.get_traces()[0]
    trace_info = trace.trace_info
    assert trace_info.request_id is not None
    assert trace_info.execution_time_ms >= 0.1 * 1e3  # at least 0.1 sec
    assert trace_info.status == TraceStatus.OK
    request_metadata_dict = {meta.key: meta.value for meta in trace_info.request_metadata}
    assert request_metadata_dict[TraceMetadataKey.INPUTS] == '{"x": 2, "y": 5}'
    assert request_metadata_dict[TraceMetadataKey.OUTPUTS] == '{"output": 64}'

    spans = trace.trace_data.spans
    assert len(spans) == 3

    span_name_to_span = {span.name: span for span in spans}
    root_span = span_name_to_span["predict"]
    assert root_span.start_time // 1e3 == trace_info.timestamp_ms
    assert root_span.parent_span_id is None
    assert root_span.inputs == {"x": 2, "y": 5}
    assert root_span.outputs == {"output": 64}
    assert root_span.attributes == {"function_name": "predict"}

    child_span_1 = span_name_to_span["add_one_with_custom_name"]
    assert child_span_1.parent_span_id == root_span.context.span_id
    assert child_span_1.inputs == {"z": 7}
    assert child_span_1.outputs == {"output": 8}
    assert child_span_1.attributes == {"function_name": "add_one", "delta": 1}

    child_span_2 = span_name_to_span["square"]
    assert child_span_2.parent_span_id == root_span.context.span_id
    assert child_span_2.inputs == {"t": 8}
    assert child_span_2.outputs == {"output": 64}
    assert child_span_2.start_time <= child_span_2.end_time - 0.1 * 1e6
    assert child_span_2.attributes == {"function_name": "square"}


def test_trace_handle_exception_during_prediction(mock_client):
    # This test is to make sure that the exception raised by the main prediction
    # logic is raised properly and the trace is still logged.
    class TestModel:
        @mlflow.trace()
        def predict(self, x, y):
            return self.some_operation_raise_error(x, y)

        @mlflow.trace()
        def some_operation_raise_error(self, x, y):
            raise ValueError("Some error")

    model = TestModel()

    try:
        model.predict(2, 5)
    except ValueError:
        pass

    # Trace should be logged even if the function fails, with status code ERROR
    trace = mlflow.get_traces()[0]
    trace_info = trace.trace_info
    assert trace_info.request_id is not None
    assert trace_info.status == TraceStatus.ERROR
    trace_metadata_dict = {meta.key: meta.value for meta in trace_info.request_metadata}
    assert trace_metadata_dict[TraceMetadataKey.INPUTS] == '{"x": 2, "y": 5}'
    assert trace_metadata_dict[TraceMetadataKey.OUTPUTS] == ""

    spans = trace.trace_data.spans
    assert len(spans) == 2


def test_trace_ignore_exception_from_tracing_logic(mock_client):
    # This test is to make sure that the main prediction logic is not affected
    # by the exception raised by the tracing logic.
    class TestModel:
        @mlflow.trace()
        def predict(self, x, y):
            return x + y

    model = TestModel()

    # Exception during span creation: no-op span wrapper created and no trace is logged
    with mock.patch("mlflow.tracing.fluent.get_tracer", side_effect=ValueError("Some error")):
        output = model.predict(2, 5)

    assert output == 7
    assert mlflow.get_traces() == []

    # Exception during inspecting inputs: trace is logged without inputs field
    with mock.patch("mlflow.tracing.utils.inspect.signature", side_effect=ValueError("Some error")):
        output = model.predict(2, 5)

    assert output == 7
    trace = mlflow.get_traces()[0]
    trace_info = trace.trace_info
    trace_metadata_dict = {meta.key: meta.value for meta in trace_info.request_metadata}
    assert trace_metadata_dict[TraceMetadataKey.INPUTS] == ""
    assert trace_metadata_dict[TraceMetadataKey.OUTPUTS] == '{"output": 7}'


def test_start_span_context_manager(mock_client):
    class TestModel:
        def predict(self, x, y):
            with mlflow.start_span(name="root_span") as root_span:
                root_span.set_inputs({"x": x, "y": y})
                z = x + y

                with mlflow.start_span(name="child_span_1", span_type=SpanType.LLM) as child_span:
                    child_span.set_inputs({"z": z})
                    z = z + 2
                    child_span.set_outputs({"output": z})
                    child_span.set_attributes({"delta": 2})

                res = self.square(z)
                root_span.set_outputs({"output": res})
            return res

        def square(self, t):
            with mlflow.start_span(name="child_span_2") as span:
                span.set_inputs({"t": t})
                res = t**2
                time.sleep(0.1)
                span.set_outputs({"output": res})
                return res

    model = TestModel()
    model.predict(1, 2)

    trace = mlflow.get_traces()[0]
    trace_info = trace.trace_info
    assert trace_info.request_id is not None
    assert trace_info.execution_time_ms >= 0.1 * 1e3  # at least 0.1 sec
    assert trace_info.status == TraceStatus.OK
    trace_metadata_dict = {meta.key: meta.value for meta in trace_info.request_metadata}
    assert trace_metadata_dict[TraceMetadataKey.INPUTS] == '{"x": 1, "y": 2}'
    assert trace_metadata_dict[TraceMetadataKey.OUTPUTS] == '{"output": 25}'

    spans = trace.trace_data.spans
    assert len(spans) == 3

    span_name_to_span = {span.name: span for span in spans}
    root_span = span_name_to_span["root_span"]
    assert root_span.start_time // 1e3 == trace_info.timestamp_ms
    assert (root_span.end_time - root_span.start_time) // 1e3 == trace_info.execution_time_ms
    assert root_span.parent_span_id is None
    assert root_span.span_type == SpanType.UNKNOWN
    assert root_span.inputs == {"x": 1, "y": 2}
    assert root_span.outputs == {"output": 25}

    child_span_1 = span_name_to_span["child_span_1"]
    assert child_span_1.parent_span_id == root_span.context.span_id
    assert child_span_1.span_type == SpanType.LLM
    assert child_span_1.inputs == {"z": 3}
    assert child_span_1.outputs == {"output": 5}
    assert child_span_1.attributes == {"delta": 2}

    child_span_2 = span_name_to_span["child_span_2"]
    assert child_span_2.parent_span_id == root_span.context.span_id
    assert child_span_2.span_type == SpanType.UNKNOWN
    assert child_span_2.inputs == {"t": 5}
    assert child_span_2.outputs == {"output": 25}
    assert child_span_2.start_time <= child_span_2.end_time - 0.1 * 1e6


def test_start_span_context_manager_with_imperative_apis(mock_client):
    # This test is to make sure that the spans created with fluent APIs and imperative APIs
    # (via MLflow client) are correctly linked together. This usage is not recommended but
    # should be supported for the advanced use cases like using LangChain callbacks as a
    # part of broader tracing.
    class TestModel:
        def __init__(self):
            self._mlflow_client = mlflow.tracking.MlflowClient()

        def predict(self, x, y):
            with mlflow.start_span(name="root_span") as root_span:
                root_span.set_inputs({"x": x, "y": y})
                z = x + y

                child_span = self._mlflow_client.start_span(
                    name="child_span_1",
                    span_type=SpanType.LLM,
                    request_id=root_span.request_id,
                    parent_span_id=root_span.span_id,
                )
                child_span.set_inputs({"z": z})

                z = z + 2
                time.sleep(0.1)

                child_span.set_outputs({"output": z})
                child_span.set_attributes({"delta": 2})
                child_span.end()

                root_span.set_outputs({"output": z})
            return z

    model = TestModel()
    model.predict(1, 2)

    trace = mlflow.get_traces()[0]
    trace_info = trace.trace_info
    assert trace_info.request_id is not None
    assert trace_info.execution_time_ms >= 0.1 * 1e3  # at least 0.1 sec
    assert trace_info.status == TraceStatus.OK
    trace_metadata_dict = {meta.key: meta.value for meta in trace_info.request_metadata}
    assert trace_metadata_dict[TraceMetadataKey.INPUTS] == '{"x": 1, "y": 2}'
    assert trace_metadata_dict[TraceMetadataKey.OUTPUTS] == '{"output": 5}'

    spans = trace.trace_data.spans
    assert len(spans) == 2

    span_name_to_span = {span.name: span for span in spans}
    root_span = span_name_to_span["root_span"]
    assert root_span.start_time // 1e3 == trace_info.timestamp_ms
    assert (root_span.end_time - root_span.start_time) // 1e3 == trace_info.execution_time_ms
    assert root_span.parent_span_id is None
    assert root_span.span_type == SpanType.UNKNOWN
    assert root_span.inputs == {"x": 1, "y": 2}
    assert root_span.outputs == {"output": 5}

    child_span_1 = span_name_to_span["child_span_1"]
    assert child_span_1.parent_span_id == root_span.context.span_id
    assert child_span_1.span_type == SpanType.LLM
    assert child_span_1.inputs == {"z": 3}
    assert child_span_1.outputs == {"output": 5}
    assert child_span_1.attributes == {"delta": 2}
