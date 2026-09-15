"""
Utility functions for Futu Agent
Provides helper functions for common operations
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


class OrderUtils:
    """Utility functions for order operations"""

    @staticmethod
    def format_order_for_display(order: Dict) -> str:
        """Format order data for display"""
        return (
            f"Order {order['order_id']}: {order['symbol']} "
            f"{order['side']} {order['filled_qty']}/{order['quantity']} @ {order['price']} "
            f"[{order['status']}]"
        )

    @staticmethod
    def calculate_order_progress(order: Dict) -> float:
        """Calculate order fill percentage"""
        if order["quantity"] == 0:
            return 0.0
        return (order["filled_qty"] / order["quantity"]) * 100

    @staticmethod
    def is_order_open(status: str) -> bool:
        """Check if order is still open (not filled or cancelled)"""
        open_statuses = ["PENDING", "AVAILABLE", "PARTIAL_FILLED"]
        return status in open_statuses

    @staticmethod
    def is_order_completed(status: str) -> bool:
        """Check if order is completed (filled or cancelled)"""
        completed_statuses = ["FILLED", "CANCELLED", "REJECTED", "EXPIRED"]
        return status in completed_statuses


class SymbolUtils:
    """Utility functions for symbol operations"""

    @staticmethod
    def format_full_symbol(code: str, market: str) -> str:
        """Format symbol with market prefix"""
        return f"{market}.{code}"

    @staticmethod
    def parse_full_symbol(full_symbol: str) -> tuple:
        """Parse full symbol into market and code"""
        parts = full_symbol.split(".")
        if len(parts) == 2:
            return parts[0], parts[1]
        return None, None

    @staticmethod
    def is_valid_hk_symbol(code: str) -> bool:
        """Validate HK stock code (5 digits)"""
        return code.isdigit() and len(code) == 5

    @staticmethod
    def is_valid_us_symbol(code: str) -> bool:
        """Validate US stock code (alphanumeric, 1-5 chars)"""
        return 1 <= len(code) <= 5 and code.isalpha()


class PositionUtils:
    """Utility functions for position operations"""

    @staticmethod
    def calculate_position_value(position: Dict) -> float:
        """Calculate total position value"""
        return position["quantity"] * position["price"]

    @staticmethod
    def calculate_position_cost(position: Dict) -> float:
        """Calculate total cost of position"""
        return position["quantity"] * position["cost_price"]

    @staticmethod
    def calculate_profit_loss(position: Dict) -> float:
        """Calculate absolute profit/loss"""
        return position["market_value"] - position["quantity"] * position["cost_price"]

    @staticmethod
    def calculate_profit_loss_ratio(position: Dict) -> float:
        """Calculate profit/loss ratio as percentage"""
        if position["cost_price"] == 0:
            return 0.0
        return ((position["price"] - position["cost_price"]) / position["cost_price"]) * 100


class TimeUtils:
    """Utility functions for time operations"""

    @staticmethod
    def parse_futu_timestamp(timestamp_str: str) -> Optional[datetime]:
        """
        Parse FutuOpenD timestamp format.
        Format example: '2024-01-15 14:30:45'
        """
        try:
            return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            logger.warning(f"Failed to parse timestamp: {timestamp_str}")
            return None

    @staticmethod
    def get_time_since_order(order_time_str: str) -> Optional[str]:
        """Get human-readable time since order was placed"""
        order_time = TimeUtils.parse_futu_timestamp(order_time_str)
        if not order_time:
            return None

        now = datetime.now()
        diff = now - order_time

        if diff.seconds < 60:
            return f"{diff.seconds}s ago"
        elif diff.seconds < 3600:
            return f"{diff.seconds // 60}m ago"
        elif diff.days == 0:
            return f"{diff.seconds // 3600}h ago"
        else:
            return f"{diff.days}d ago"


class FilterUtils:
    """Utility functions for filtering operations"""

    @staticmethod
    def filter_orders_by_symbol(orders: List[Dict], symbol: str) -> List[Dict]:
        """Filter orders by symbol"""
        return [order for order in orders if order["symbol"] == symbol]

    @staticmethod
    def filter_orders_by_side(orders: List[Dict], side: str) -> List[Dict]:
        """Filter orders by side (BUY/SELL)"""
        return [order for order in orders if order["side"].upper() == side.upper()]

    @staticmethod
    def filter_orders_by_date_range(
        orders: List[Dict], start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """Filter orders by date range"""
        result = []
        for order in orders:
            order_time = TimeUtils.parse_futu_timestamp(order["order_time"])
            if order_time and start_date <= order_time <= end_date:
                result.append(order)
        return result

    @staticmethod
    def filter_positions_by_profit(
        positions: List[Dict], min_profit: float = None, max_profit: float = None
    ) -> List[Dict]:
        """Filter positions by profit/loss range"""
        result = []
        for pos in positions:
            pnl = pos["profit_loss"]
            if (min_profit is None or pnl >= min_profit) and (
                max_profit is None or pnl <= max_profit
            ):
                result.append(pos)
        return result


class ValidationUtils:
    """Utility functions for validation"""

    @staticmethod
    def validate_order_params(
        symbol: str, side: str, quantity: int, price: float
    ) -> tuple:
        """
        Validate order parameters.
        Returns: (is_valid, error_message)
        """
        if not symbol:
            return False, "Symbol cannot be empty"

        if side.upper() not in ["BUY", "SELL"]:
            return False, "Side must be BUY or SELL"

        if quantity <= 0:
            return False, "Quantity must be positive"

        if price <= 0:
            return False, "Price must be positive"

        return True, None

    @staticmethod
    def validate_available_balance(account_cash: float, order_cost: float) -> bool:
        """Check if account has sufficient balance for order"""
        return account_cash >= order_cost


class ReportUtils:
    """Utility functions for generating reports"""

    @staticmethod
    def generate_positions_report(positions: List[Dict]) -> str:
        """Generate a text report of current positions"""
        if not positions:
            return "No positions"

        report = "=== POSITIONS REPORT ===\n"
        total_market_value = 0
        total_cost = 0

        for pos in positions:
            cost = pos["quantity"] * pos["cost_price"]
            market_val = pos["market_value"]
            total_market_value += market_val
            total_cost += cost

            report += f"\n{pos['symbol']}\n"
            report += f"  Qty: {pos['quantity']} @ {pos['price']}\n"
            report += f"  Market Value: {market_val:.2f}\n"
            report += f"  P&L: {pos['profit_loss']:.2f} ({pos['profit_loss_ratio']:.2f}%)\n"

        report += f"\n--- TOTALS ---\n"
        report += f"Total Market Value: {total_market_value:.2f}\n"
        report += f"Total Cost: {total_cost:.2f}\n"
        report += f"Total P&L: {total_market_value - total_cost:.2f}\n"

        return report

    @staticmethod
    def generate_orders_report(orders: List[Dict]) -> str:
        """Generate a text report of orders"""
        if not orders:
            return "No orders"

        report = "=== ORDERS REPORT ===\n"

        for order in orders:
            fill_pct = (order["filled_qty"] / order["quantity"] * 100) if order["quantity"] > 0 else 0
            report += f"\n{order['order_id']}: {order['symbol']}\n"
            report += f"  {order['side']} {order['quantity']} @ {order['price']}\n"
            report += f"  Filled: {order['filled_qty']}/{order['quantity']} ({fill_pct:.1f}%)\n"
            report += f"  Status: {order['status']}\n"

        return report
