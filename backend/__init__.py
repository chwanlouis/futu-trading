"""
Futu Trading Agent Backend
A Python-based trading agent for FutuOpenD
"""

from .futu_agent import FutuAgent, MarketType, OrderStatusEnum
from .config import Config
from .utils import (
    OrderUtils,
    SymbolUtils,
    PositionUtils,
    TimeUtils,
    FilterUtils,
    ValidationUtils,
    ReportUtils,
)

__version__ = "1.0.0"
__author__ = "Futu Trading Team"
__all__ = [
    "FutuAgent",
    "MarketType",
    "OrderStatusEnum",
    "Config",
    "OrderUtils",
    "SymbolUtils",
    "PositionUtils",
    "TimeUtils",
    "FilterUtils",
    "ValidationUtils",
    "ReportUtils",
]
