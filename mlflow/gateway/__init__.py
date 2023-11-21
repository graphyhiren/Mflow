"""
.. warning::

    `mlflow.gateway` is deprecated and will be replaced by the deployments API in a future release.
    See :ref:`gateway-deprecation` for more details.",
"""
import warnings

from mlflow.gateway.client import MlflowGatewayClient
from mlflow.gateway.fluent import (
    create_route,
    delete_route,
    get_limits,
    get_route,
    query,
    search_routes,
    set_limits,
)
from mlflow.gateway.utils import get_gateway_uri, set_gateway_uri

warnings.warn(
    "`mlflow.gateway` is deprecated and will be replaced by the deployments API in a future "
    "release.  See https://mlflow.org/docs/latest/llms/gateway/deprecation.html for more details.",
    FutureWarning,
)

__all__ = [
    "create_route",
    "delete_route",
    "get_route",
    "set_limits",
    "get_limits",
    "get_gateway_uri",
    "MlflowGatewayClient",
    "query",
    "search_routes",
    "set_gateway_uri",
]
