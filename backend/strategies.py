"""
Advanced Trading Strategies Module
Provides higher-level trading strategies built on top of FutuAgent
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from futu_agent import FutuAgent, MarketType, OrderStatusEnum


logger = logging.getLogger(__name__)


class TradingStrategy:
    """Base class for trading strategies"""

    def __init__(self, agent: FutuAgent, name: str):
        """
        Initialize strategy.

        Args:
            agent: FutuAgent instance
            name: Strategy name
        """
        self.agent = agent
        self.name = name
        self.active = False
        self.created_at = datetime.now()

    def start(self):
        """Start the strategy"""
        self.active = True
        logger.info(f"Strategy {self.name} started")

    def stop(self):
        """Stop the strategy"""
        self.active = False
        logger.info(f"Strategy {self.name} stopped")

    def execute(self):
        """Execute strategy logic - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement execute()")


class GridTradingStrategy(TradingStrategy):
    """
    Grid Trading Strategy
    Places multiple buy and sell orders at different price levels
    """

    def __init__(
        self,
        agent: FutuAgent,
        symbol: str,
        market: MarketType,
        base_price: float,
        grid_size: int = 5,
        grid_step: float = 1.0,
        quantity_per_grid: int = 10,
    ):
        """
        Initialize grid trading strategy.

        Args:
            agent: FutuAgent instance
            symbol: Trading symbol
            market: Market (HK or US)
            base_price: Base price for grid
            grid_size: Number of grid levels above and below base
            grid_step: Price step between grid levels
            quantity_per_grid: Order quantity per grid level
        """
        super().__init__(agent, "GridTrading")
        self.symbol = symbol
        self.market = market
        self.base_price = base_price
        self.grid_size = grid_size
        self.grid_step = grid_step
        self.quantity_per_grid = quantity_per_grid
        self.orders = []

    def execute(self):
        """Execute grid trading strategy"""
        if not self.active:
            return False

        logger.info(f"Executing grid trading for {self.symbol}")

        # Place buy orders below base price
        for i in range(1, self.grid_size + 1):
            buy_price = self.base_price - (i * self.grid_step)
            success, order_id = self.agent.place_order(
                symbol_code=self.symbol,
                market=self.market,
                side="BUY",
                quantity=self.quantity_per_grid,
                price=buy_price,
            )
            if success:
                self.orders.append({"order_id": order_id, "type": "BUY", "price": buy_price})

        # Place sell orders above base price
        for i in range(1, self.grid_size + 1):
            sell_price = self.base_price + (i * self.grid_step)
            success, order_id = self.agent.place_order(
                symbol_code=self.symbol,
                market=self.market,
                side="SELL",
                quantity=self.quantity_per_grid,
                price=sell_price,
            )
            if success:
                self.orders.append({"order_id": order_id, "type": "SELL", "price": sell_price})

        logger.info(f"Grid trading: placed {len(self.orders)} orders")
        return True

    def cancel_all_orders(self):
        """Cancel all grid orders"""
        for order_info in self.orders:
            self.agent.cancel_order(order_info["order_id"])
        self.orders.clear()
        logger.info(f"Cancelled all grid orders for {self.symbol}")


class DollarCostAveragingStrategy(TradingStrategy):
    """
    Dollar Cost Averaging Strategy
    Invests a fixed amount at regular intervals
    """

    def __init__(
        self,
        agent: FutuAgent,
        symbol: str,
        market: MarketType,
        investment_amount: float,
        target_price: Optional[float] = None,
    ):
        """
        Initialize DCA strategy.

        Args:
            agent: FutuAgent instance
            symbol: Trading symbol
            market: Market (HK or US)
            investment_amount: Amount to invest in each purchase
            target_price: Optional target price for purchase
        """
        super().__init__(agent, "DollarCostAveraging")
        self.symbol = symbol
        self.market = market
        self.investment_amount = investment_amount
        self.target_price = target_price
        self.purchase_history = []

    def execute(self):
        """Execute DCA strategy"""
        if not self.active:
            return False

        logger.info(f"Executing DCA for {self.symbol}")

        # Get current price
        symbol_details = self.agent.get_symbol_details(self.symbol, self.market)
        if not symbol_details:
            logger.error(f"Could not get price for {self.symbol}")
            return False

        # Check if price meets target (if set)
        current_price = symbol_details.get("price", self.target_price)
        if self.target_price and current_price > self.target_price:
            logger.info(f"Current price {current_price} exceeds target {self.target_price}")
            return False

        # Calculate quantity
        quantity = int(self.investment_amount / current_price)
        if quantity <= 0:
            logger.error(f"Investment amount too low for current price")
            return False

        # Place order
        success, order_id = self.agent.place_order(
            symbol_code=self.symbol,
            market=self.market,
            side="BUY",
            quantity=quantity,
            price=current_price,
        )

        if success:
            self.purchase_history.append(
                {
                    "order_id": order_id,
                    "quantity": quantity,
                    "price": current_price,
                    "timestamp": datetime.now(),
                }
            )
            logger.info(f"DCA purchase: {quantity} shares @ {current_price}")
            return True

        return False

    def get_average_cost(self) -> float:
        """Calculate average purchase cost"""
        if not self.purchase_history:
            return 0.0

        total_cost = sum(p["quantity"] * p["price"] for p in self.purchase_history)
        total_quantity = sum(p["quantity"] for p in self.purchase_history)

        return total_cost / total_quantity if total_quantity > 0 else 0.0


class StopLossStrategy(TradingStrategy):
    """
    Stop Loss Strategy
    Automatically sells positions when price drops below threshold
    """

    def __init__(
        self,
        agent: FutuAgent,
        symbol: str,
        market: MarketType,
        stop_loss_percent: float = 5.0,
    ):
        """
        Initialize stop loss strategy.

        Args:
            agent: FutuAgent instance
            symbol: Trading symbol
            market: Market (HK or US)
            stop_loss_percent: Stop loss percentage (e.g., 5 for 5% loss)
        """
        super().__init__(agent, "StopLoss")
        self.symbol = symbol
        self.market = market
        self.stop_loss_percent = stop_loss_percent
        self.entry_price = None

    def set_entry_price(self, price: float):
        """Set the entry price for stop loss calculation"""
        self.entry_price = price
        stop_price = price * (1 - self.stop_loss_percent / 100)
        logger.info(f"Stop loss set at {stop_price} ({self.stop_loss_percent}% below entry)")

    def execute(self):
        """Execute stop loss strategy"""
        if not self.active or not self.entry_price:
            return False

        logger.info(f"Checking stop loss for {self.symbol}")

        # Get positions
        positions = self.agent.get_positions()
        position = next((p for p in positions if p["symbol"] == self.symbol), None)

        if not position:
            logger.warning(f"No position found for {self.symbol}")
            return False

        current_price = position["price"]
        stop_price = self.entry_price * (1 - self.stop_loss_percent / 100)

        if current_price <= stop_price:
            logger.warning(f"Stop loss triggered! Selling {position['quantity']} @ {current_price}")
            success, order_id = self.agent.place_order(
                symbol_code=self.symbol,
                market=self.market,
                side="SELL",
                quantity=position["available_qty"],
                price=current_price,
            )
            return success

        return False


class StrategyManager:
    """Manages multiple trading strategies"""

    def __init__(self, agent: FutuAgent):
        """
        Initialize strategy manager.

        Args:
            agent: FutuAgent instance
        """
        self.agent = agent
        self.strategies: Dict[str, TradingStrategy] = {}

    def add_strategy(self, strategy_id: str, strategy: TradingStrategy):
        """Add a strategy"""
        self.strategies[strategy_id] = strategy
        logger.info(f"Strategy added: {strategy_id}")

    def remove_strategy(self, strategy_id: str):
        """Remove a strategy"""
        if strategy_id in self.strategies:
            self.strategies[strategy_id].stop()
            del self.strategies[strategy_id]
            logger.info(f"Strategy removed: {strategy_id}")

    def start_strategy(self, strategy_id: str):
        """Start a specific strategy"""
        if strategy_id in self.strategies:
            self.strategies[strategy_id].start()

    def stop_strategy(self, strategy_id: str):
        """Stop a specific strategy"""
        if strategy_id in self.strategies:
            self.strategies[strategy_id].stop()

    def start_all(self):
        """Start all strategies"""
        for strategy in self.strategies.values():
            strategy.start()

    def stop_all(self):
        """Stop all strategies"""
        for strategy in self.strategies.values():
            strategy.stop()

    def execute_all(self):
        """Execute all active strategies"""
        for strategy_id, strategy in self.strategies.items():
            if strategy.active:
                try:
                    strategy.execute()
                except Exception as e:
                    logger.error(f"Error executing strategy {strategy_id}: {e}")

    def get_status(self) -> Dict:
        """Get status of all strategies"""
        return {
            strategy_id: {
                "name": strategy.name,
                "active": strategy.active,
                "created_at": strategy.created_at,
            }
            for strategy_id, strategy in self.strategies.items()
        }
