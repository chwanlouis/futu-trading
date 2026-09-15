"""
Unit tests for Futu Agent
Tests for core functionality of FutuAgent
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from futu_agent import FutuAgent, MarketType, OrderStatusEnum


class TestFutuAgentConnection(unittest.TestCase):
    """Test connection methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.agent = FutuAgent(host="127.0.0.1", port=11111)

    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.host, "127.0.0.1")
        self.assertEqual(self.agent.port, 11111)
        self.assertFalse(self.agent.is_connected())

    @patch("futu_agent.OpenQuoteContext")
    @patch("futu_agent.OpenTradeContext")
    def test_connect_success(self, mock_trade, mock_quote):
        """Test successful connection"""
        self.assertTrue(self.agent.connect())
        self.assertTrue(self.agent.is_connected())

    @patch("futu_agent.OpenQuoteContext")
    @patch("futu_agent.OpenTradeContext")
    def test_connect_failure(self, mock_trade, mock_quote):
        """Test connection failure"""
        mock_quote.side_effect = Exception("Connection refused")
        self.assertFalse(self.agent.connect())
        self.assertFalse(self.agent.is_connected())

    def test_disconnect(self):
        """Test disconnection"""
        self.agent.quote_ctx = Mock()
        self.agent.trade_ctx = Mock()
        self.agent._connected = True

        self.assertTrue(self.agent.disconnect())
        self.assertFalse(self.agent.is_connected())


class TestSymbolManagement(unittest.TestCase):
    """Test symbol management functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.agent = FutuAgent()
        self.agent._connected = True
        self.agent.quote_ctx = Mock()
        self.agent.trade_ctx = Mock()

    def test_get_tradable_symbols_not_connected(self):
        """Test get_tradable_symbols when not connected"""
        self.agent._connected = False
        result = self.agent.get_tradable_symbols()
        self.assertEqual(result, {})

    @patch("futu_agent.RET_OK", 0)
    def test_get_tradable_symbols_hk(self, *args):
        """Test getting HK symbols"""
        # This would require mocking the return value
        # Implementation depends on actual FutuOpenD API
        pass

    def test_get_symbol_details_not_connected(self):
        """Test get_symbol_details when not connected"""
        self.agent._connected = False
        result = self.agent.get_symbol_details("00700", MarketType.HK)
        self.assertIsNone(result)


class TestOrderManagement(unittest.TestCase):
    """Test order management functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.agent = FutuAgent()
        self.agent._connected = True
        self.agent.quote_ctx = Mock()
        self.agent.trade_ctx = Mock()

    def test_get_orders_not_connected(self):
        """Test get_orders when not connected"""
        self.agent._connected = False
        result = self.agent.get_orders()
        self.assertEqual(result, [])

    def test_map_order_status(self):
        """Test order status mapping"""
        self.assertEqual(
            self.agent._map_order_status("FILLED"),
            OrderStatusEnum.FILLED.value
        )
        self.assertEqual(
            self.agent._map_order_status("CANCELLED"),
            OrderStatusEnum.CANCELLED.value
        )
        self.assertEqual(
            self.agent._map_order_status("SUBMITTED"),
            OrderStatusEnum.PENDING.value
        )

    def test_get_pending_orders_filters_correctly(self):
        """Test that get_pending_orders filters correctly"""
        # Mock orders
        self.agent.get_orders = Mock(return_value=[
            {"order_id": "1", "status": "PENDING"},
            {"order_id": "2", "status": "FILLED"},
            {"order_id": "3", "status": "PENDING"},
        ])

        result = self.agent.get_pending_orders()
        # Should filter by PENDING status
        self.assertEqual(len(result), 2)


class TestOrderPlacement(unittest.TestCase):
    """Test order placement functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.agent = FutuAgent()
        self.agent._connected = True
        self.agent.quote_ctx = Mock()
        self.agent.trade_ctx = Mock()

    def test_place_order_not_connected(self):
        """Test place_order when not connected"""
        self.agent._connected = False
        success, result = self.agent.place_order(
            symbol_code="00700",
            market=MarketType.HK,
            side="BUY",
            quantity=100,
            price=300.0
        )
        self.assertFalse(success)
        self.assertIn("not connected", result.lower())

    def test_cancel_order_not_connected(self):
        """Test cancel_order when not connected"""
        self.agent._connected = False
        success, result = self.agent.cancel_order("12345")
        self.assertFalse(success)
        self.assertIn("not connected", result.lower())


class TestAccountManagement(unittest.TestCase):
    """Test account management functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.agent = FutuAgent()
        self.agent._connected = True
        self.agent.quote_ctx = Mock()
        self.agent.trade_ctx = Mock()

    def test_get_account_info_not_connected(self):
        """Test get_account_info when not connected"""
        self.agent._connected = False
        result = self.agent.get_account_info()
        self.assertIsNone(result)

    def test_get_positions_not_connected(self):
        """Test get_positions when not connected"""
        self.agent._connected = False
        result = self.agent.get_positions()
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
