# Quick Start Guide - Futu Trading Agent

Get up and running with the Futu Trading Agent in 5 minutes!

## Prerequisites

- Python 3.7 or higher
- FutuOpenD installed and running (listening on 127.0.0.1:11111)
- pip package manager

## Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Step 2: Configure Connection

Copy the example environment file and update with your settings:

```bash
cp .env.example .env
```

Edit `.env` and ensure FutuOpenD connection settings are correct:
```env
FUTU_HOST=127.0.0.1
FUTU_PORT=11111
```

## Step 3: Basic Usage

### Get Tradable Symbols

```python
from futu_agent import FutuAgent, MarketType

agent = FutuAgent()
agent.connect()

# Get all tradable symbols
symbols = agent.get_tradable_symbols()
print(f"HK Symbols: {symbols['HK'][:10]}")  # First 10 HK stocks
print(f"US Symbols: {symbols['US'][:10]}")  # First 10 US stocks

agent.disconnect()
```

### Get Orders

```python
from futu_agent import FutuAgent

agent = FutuAgent()
agent.connect()

# Get all orders
orders = agent.get_orders()

# Get pending orders only
pending = agent.get_pending_orders()

# Get filled orders only
filled = agent.get_filled_orders()

for order in orders:
    print(f"{order['order_id']}: {order['symbol']} {order['side']} {order['status']}")

agent.disconnect()
```

### Place Order

```python
from futu_agent import FutuAgent, MarketType

agent = FutuAgent()
agent.connect()

# Place a buy order for HK stock
success, result = agent.place_order(
    symbol_code="00700",          # Tencent in HK
    market=MarketType.HK,
    side="BUY",
    quantity=100,
    price=300.0
)

if success:
    print(f"Order placed successfully! Order ID: {result}")
else:
    print(f"Failed to place order: {result}")

agent.disconnect()
```

## Step 4: Run Examples

For comprehensive examples, run the included example script:

```bash
python example_usage.py
```

This demonstrates:
- Getting symbols for HK and US markets
- Querying account information
- Retrieving positions
- Getting orders by status
- Account details and position management

## Common Tasks

### Get Account Information

```python
account = agent.get_account_info()
print(f"Cash: {account['cash']}")
print(f"Total Assets: {account['total_assets']}")
```

### Get Current Positions

```python
positions = agent.get_positions()
for pos in positions:
    print(f"{pos['symbol']}: {pos['quantity']} shares @ {pos['price']}")
```

### Cancel an Order

```python
success, message = agent.cancel_order(order_id="1234567890")
if success:
    print(f"Order cancelled: {message}")
```

### Get Symbol Details

```python
symbol_detail = agent.get_symbol_details("00700", MarketType.HK)
print(f"Code: {symbol_detail['code']}")
print(f"Name: {symbol_detail['name']}")
print(f"Lot Size: {symbol_detail['lot_size']}")
```

## Using Utilities

The `utils` module provides helper functions:

```python
from utils import OrderUtils, PositionUtils

# Check order progress
progress = OrderUtils.calculate_order_progress(order)
print(f"Order is {progress}% filled")

# Calculate position P&L
pnl = PositionUtils.calculate_profit_loss(position)
print(f"Profit/Loss: {pnl}")

# Generate position report
from utils import ReportUtils
report = ReportUtils.generate_positions_report(positions)
print(report)
```

## Using Trading Strategies

```python
from futu_agent import FutuAgent, MarketType
from strategies import GridTradingStrategy, StrategyManager

agent = FutuAgent()
agent.connect()

# Create and manage strategies
manager = StrategyManager(agent)

# Add grid trading strategy
grid_strategy = GridTradingStrategy(
    agent=agent,
    symbol="00700",
    market=MarketType.HK,
    base_price=300.0,
    grid_size=5,
    grid_step=1.0,
    quantity_per_grid=10
)
manager.add_strategy("grid_1", grid_strategy)

# Start the strategy
manager.start_strategy("grid_1")
manager.execute_all()

# Check status
print(manager.get_status())

agent.disconnect()
```

## Troubleshooting

### Connection Failed
- Ensure FutuOpenD is running on the configured host/port
- Check firewall settings
- Verify connection parameters in `.env`

### Import Errors
- Make sure dependencies are installed: `pip install -r requirements.txt`
- Check that you're in the backend directory

### Order Placement Failed
- Verify sufficient account balance
- Check that the market is open
- Ensure the symbol is tradable
- Verify correct symbol format (HK: 5 digits, US: 1-5 letters)

## Next Steps

1. Read the full [README.md](README.md) for comprehensive API documentation
2. Check [example_usage.py](example_usage.py) for detailed examples
3. Review [utils.py](utils.py) for available helper functions
4. Explore [strategies.py](strategies.py) for advanced trading strategies
5. Run tests: `python -m pytest test_futu_agent.py`

## Support

For issues or questions:
- Check the README.md for detailed documentation
- Review example_usage.py for code examples
- Check test_futu_agent.py for usage patterns
- Ensure FutuOpenD is properly configured and running

Happy trading! 🚀
