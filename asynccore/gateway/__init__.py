"""
Module responsible for communication with the gateway
"""

from .gateway import GatewayConnection, GatewayResponse, Gateway

__all__: tuple[str, str, str] = (
    "GatewayConnection",
    "GatewayResponse",
    "Gateway"
)
