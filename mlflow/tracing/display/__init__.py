from mlflow.tracing.display.display_client import IPythonTraceDisplayHandler

__all__ = ["IPythonTraceDisplayHandler", "get_display_handler"]


def get_display_handler() -> IPythonTraceDisplayHandler:
    return IPythonTraceDisplayHandler.get_instance()
