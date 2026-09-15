"""
Futu Agent - Core module for trading operations with FutuOpenD
"""

import logging
from typing import List, Dict, Optional, Tuple
from enum import Enum
from futu import OpenQuoteContext, OpenTradeContext, RET_OK, TrdSide, TrdStatus, Market


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketType(Enum):
    """Supported market types"""
    HK = "HK"
    US = "US"


class OrderStatusEnum(Enum):
    """Order status types"""
    PENDING = "PENDING"
    AVAILABLE = "AVAILABLE"
    PARTIAL_FILLED = "PARTIAL_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class FutuAgent:
    """
    Futu Agent for trading operations.
    Handles connection to FutuOpenD and provides methods for:
    - Getting tradable symbols
    - Managing orders
    - Placing orders
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 11111):
        """
        Initialize FutuAgent with connection parameters.

        Args:
            host: FutuOpenD host address (default: localhost)
            port: FutuOpenD port (default: 11111)
        """
        self.host = host
        self.port = port
        self.quote_ctx = None
        self.trade_ctx = None
        self._connected = False

    def connect(self) -> bool:
        """
        Establish connection to FutuOpenD.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.quote_ctx = OpenQuoteContext(host=self.host, port=self.port)
            self.trade_ctx = OpenTradeContext(host=self.host, port=self.port)
            self._connected = True
            logger.info(f"Connected to FutuOpenD at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to FutuOpenD: {e}")
            self._connected = False
            return False

    def disconnect(self) -> bool:
        """
        Disconnect from FutuOpenD.

        Returns:
            bool: True if disconnection successful
        """
        try:
            if self.quote_ctx:
                self.quote_ctx.close()
            if self.trade_ctx:
                self.trade_ctx.close()
            self._connected = False
            logger.info("Disconnected from FutuOpenD")
            return True
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
            return False

    def is_connected(self) -> bool:
        """Check if agent is connected to FutuOpenD"""
        return self._connected

    # ========== Symbol Management ==========

    def get_tradable_symbols(
        self, market: Optional[MarketType] = None
    ) -> Dict[str, List[str]]:
        """
        Get tradable symbols for specified markets.

        Args:
            market: Market type (MarketType.HK, MarketType.US, or None for both)

        Returns:
            Dictionary with market as key and list of symbols as value
            Example: {'HK': ['00001', '00700'], 'US': ['AAPL', 'MSFT']}
        """
        if not self.is_connected():
            logger.error("Agent not connected. Call connect() first.")
            return {}

        result = {}

        try:
            # Get HK symbols
            if market is None or market == MarketType.HK:
                ret, hk_symbols = self.quote_ctx.get_stock_basicinfo(Market.HK)
                if ret == RET_OK:
                    hk_list = [row[1] for row in hk_symbols.values]
                    result[MarketType.HK.value] = hk_list
                    logger.info(f"Retrieved {len(hk_list)} HK tradable symbols")
                else:
                    logger.error(f"Failed to get HK symbols: {ret}")
                    result[MarketType.HK.value] = []

            # Get US symbols
            if market is None or market == MarketType.US:
                ret, us_symbols = self.quote_ctx.get_stock_basicinfo(Market.US)
                if ret == RET_OK:
                    us_list = [row[1] for row in us_symbols.values]
                    result[MarketType.US.value] = us_list
                    logger.info(f"Retrieved {len(us_list)} US tradable symbols")
                else:
                    logger.error(f"Failed to get US symbols: {ret}")
                    result[MarketType.US.value] = []

        except Exception as e:
            logger.error(f"Error getting tradable symbols: {e}")

        return result

    def get_symbol_details(
        self, symbol_code: str, market: MarketType
    ) -> Optional[Dict]:
        """
        Get details for a specific symbol.

        Args:
            symbol_code: Symbol code (e.g., '00700' for HK, 'AAPL' for US)
            market: Market type

        Returns:
            Dictionary with symbol details or None if not found
        """
        if not self.is_connected():
            logger.error("Agent not connected. Call connect() first.")
            return None

        try:
            market_enum = Market.HK if market == MarketType.HK else Market.US
            ret, symbol_data = self.quote_ctx.get_stock_basicinfo(market_enum)

            if ret == RET_OK:
                for row in symbol_data.values:
                    if row[1] == symbol_code:
                        return {
                            "code": row[1],
                            "name": row[2],
                            "lot_size": row[3],
                            "security_type": row[4],
                            "market": market.value,
                        }
            logger.warning(f"Symbol {symbol_code} not found in {market.value}")
        except Exception as e:
            logger.error(f"Error getting symbol details: {e}")

        return None

    # ========== Order Management ==========

    def get_orders(
        self,
        status_filter: Optional[OrderStatusEnum] = None,
        refresh: bool = True,
    ) -> List[Dict]:
        """
        Get orders with optional status filtering.

        Args:
            status_filter: Filter by specific order status, None for all orders
            refresh: Force refresh from server

        Returns:
            List of order dictionaries with details
        """
        if not self.is_connected():
            logger.error("Agent not connected. Call connect() first.")
            return []

        try:
            ret, orders = self.trade_ctx.order_list_query(refresh=refresh)

            if ret != RET_OK:
                logger.error(f"Failed to query orders: {ret}")
                return []

            order_list = []
            for _, order_row in orders.iterrows():
                order_dict = {
                    "order_id": order_row["Order ID"],
                    "symbol": order_row["Code"],
                    "side": order_row["Trd_side"],
                    "status": self._map_order_status(order_row["Order Status"]),
                    "quantity": order_row["Qty"],
                    "filled_qty": order_row["Dealt Qty"],
                    "price": order_row["Price"],
                    "filled_price": order_row["Dealt Avg Price"],
                    "order_time": order_row["Create Time"],
                    "last_update": order_row["Last Update Time"],
                }

                # Apply status filter if provided
                if status_filter is None or order_dict["status"] == status_filter.value:
                    order_list.append(order_dict)

            logger.info(f"Retrieved {len(order_list)} orders")
            return order_list

        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []

    def get_order_by_id(self, order_id: str) -> Optional[Dict]:
        """
        Get specific order details by order ID.

        Args:
            order_id: Order ID

        Returns:
            Order dictionary or None if not found
        """
        orders = self.get_orders(refresh=True)
        for order in orders:
            if order["order_id"] == order_id:
                return order
        return None

    def get_pending_orders(self) -> List[Dict]:
        """Get all pending orders (not filled/cancelled)"""
        return self.get_orders(status_filter=OrderStatusEnum.PENDING)

    def get_filled_orders(self) -> List[Dict]:
        """Get all filled orders"""
        return self.get_orders(status_filter=OrderStatusEnum.FILLED)

    def get_cancelled_orders(self) -> List[Dict]:
        """Get all cancelled orders"""
        return self.get_orders(status_filter=OrderStatusEnum.CANCELLED)

    @staticmethod
    def _map_order_status(futu_status: str) -> str:
        """
        Map FutuOpenD order status to our OrderStatusEnum.

        Args:
            futu_status: Status from FutuOpenD

        Returns:
            Mapped status string
        """
        status_map = {
            "SUBMITTED": OrderStatusEnum.PENDING.value,
            "PENDING_SUBMIT": OrderStatusEnum.PENDING.value,
            "FILLED": OrderStatusEnum.FILLED.value,
            "PARTIALLY_FILLED": OrderStatusEnum.PARTIAL_FILLED.value,
            "CANCELLED": OrderStatusEnum.CANCELLED.value,
            "REJECTED": OrderStatusEnum.REJECTED.value,
            "EXPIRED": OrderStatusEnum.EXPIRED.value,
        }
        return status_map.get(futu_status, futu_status)

    # ========== Order Placement ==========

    def place_order(
        self,
        symbol_code: str,
        market: MarketType,
        side: str,
        quantity: int,
        price: float,
        order_type: str = "NORMAL",
    ) -> Tuple[bool, Optional[str]]:
        """
        Place a new order.

        Args:
            symbol_code: Symbol code (e.g., '00700' for HK, 'AAPL' for US)
            market: Market type
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            price: Order price
            order_type: Order type (default: 'NORMAL')

        Returns:
            Tuple of (success: bool, order_id: str or error_message: str)
        """
        if not self.is_connected():
            return False, "Agent not connected. Call connect() first."

        try:
            # Construct full symbol code
            if market == MarketType.HK:
                symbol_full = f"HK.{symbol_code}"
            else:
                symbol_full = f"US.{symbol_code}"

            # Map side to TrdSide
            trd_side = TrdSide.BUY if side.upper() == "BUY" else TrdSide.SELL

            # Place order
            ret, order_id = self.trade_ctx.place_order(
                price=price,
                qty=quantity,
                code=symbol_full,
                trd_side=trd_side,
                order_type=order_type,
            )

            if ret == RET_OK:
                logger.info(
                    f"Order placed successfully. Order ID: {order_id}, "
                    f"Symbol: {symbol_code}, Side: {side}, Qty: {quantity}, Price: {price}"
                )
                return True, order_id
            else:
                error_msg = f"Failed to place order: {ret}"
                logger.error(error_msg)
                return False, error_msg

        except Exception as e:
            error_msg = f"Error placing order: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def cancel_order(self, order_id: str) -> Tuple[bool, Optional[str]]:
        """
        Cancel an existing order.

        Args:
            order_id: Order ID to cancel

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.is_connected():
            return False, "Agent not connected. Call connect() first."

        try:
            ret = self.trade_ctx.cancel_order(order_id=order_id)

            if ret == RET_OK:
                logger.info(f"Order cancelled successfully. Order ID: {order_id}")
                return True, f"Order {order_id} cancelled"
            else:
                error_msg = f"Failed to cancel order: {ret}"
                logger.error(error_msg)
                return False, error_msg

        except Exception as e:
            error_msg = f"Error cancelling order: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    # ========== Account Information ==========

    def get_account_info(self) -> Optional[Dict]:
        """
        Get account information including cash, positions, etc.

        Returns:
            Dictionary with account details or None on error
        """
        if not self.is_connected():
            logger.error("Agent not connected. Call connect() first.")
            return None

        try:
            ret, account_data = self.trade_ctx.accinfo_query()

            if ret == RET_OK:
                return {
                    "currency": account_data.iloc[0]["Currency"],
                    "cash": account_data.iloc[0]["Cash"],
                    "available_cash": account_data.iloc[0]["AvailableCash"],
                    "market_value": account_data.iloc[0]["MarketVal"],
                    "total_assets": account_data.iloc[0]["TotalAssets"],
                }
            else:
                logger.error(f"Failed to get account info: {ret}")
                return None

        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None

    def get_positions(self) -> List[Dict]:
        """
        Get current positions.

        Returns:
            List of position dictionaries
        """
        if not self.is_connected():
            logger.error("Agent not connected. Call connect() first.")
            return []

        try:
            ret, positions = self.trade_ctx.position_list_query()

            if ret != RET_OK:
                logger.error(f"Failed to query positions: {ret}")
                return []

            position_list = []
            for _, pos_row in positions.iterrows():
                position_dict = {
                    "symbol": pos_row["Code"],
                    "quantity": pos_row["Qty"],
                    "available_qty": pos_row["AvailQty"],
                    "price": pos_row["Price"],
                    "cost_price": pos_row["CostPrice"],
                    "market_value": pos_row["MarketVal"],
                    "profit_loss": pos_row["PnL"],
                    "profit_loss_ratio": pos_row["PnL%"],
                }
                position_list.append(position_dict)

            logger.info(f"Retrieved {len(position_list)} positions")
            return position_list

        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
