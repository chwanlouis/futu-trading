# Futu Trading Agent Backend

A Python-based trading agent for interacting with FutuOpenD (Futu OpenD). This backend provides a simple and comprehensive interface for trading operations including symbol management, order management, and account information.

## Features

### 1. Symbol Management
- Get tradable symbols for HK (Hong Kong) and US stock markets
- Filter by specific market
- Retrieve symbol details (name, lot size, security type, etc.)

### 2. Order Management
- Get all orders with status filtering
- Support for multiple order statuses:
  - PENDING
  - AVAILABLE
  - PARTIAL_FILLED
  - FILLED
  - CANCELLED
  - REJECTED
  - EXPIRED
- Retrieve orders by ID
- Get pending, filled, or cancelled orders specifically
- Query order history with refresh option

### 3. Order Placement
- Place buy/sell orders
- Cancel existing orders
- Support for both HK and US markets
- Configurable order types

### 4. Account Management
- Get account information (cash, available cash, market value, total assets)
- Get current positions
- View position details (quantity, price, profit/loss)

## Installation

### Prerequisites
- Python 3.7+
- FutuOpenD installed and running on your system
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your FutuOpenD connection settings
```

## Configuration

The agent uses environment variables for configuration. Create a `.env` file based on `.env.example`:

```env
# FutuOpenD Connection Settings
FUTU_HOST=127.0.0.1
FUTU_PORT=11111

# Logging Configuration
LOG_LEVEL=INFO

# Trading Settings
DEFAULT_MARKET=HK
ORDER_TIMEOUT=30

# API Settings
MAX_RETRIES=3
RETRY_DELAY=1

# Environment
ENVIRONMENT=development
```

## Usage

### Basic Setup

```python
from futu_agent import FutuAgent, MarketType

# Initialize the agent
agent = FutuAgent(host="127.0.0.1", port=11111)

# Connect to FutuOpenD
if agent.connect():
    print("Connected successfully")
else:
    print("Connection failed")
```

### Get Tradable Symbols

```python
# Get symbols for both markets
symbols = agent.get_tradable_symbols()
print(f"HK Symbols: {symbols['HK']}")
print(f"US Symbols: {symbols['US']}")

# Get symbols for specific market
hk_symbols = agent.get_tradable_symbols(market=MarketType.HK)
us_symbols = agent.get_tradable_symbols(market=MarketType.US)

# Get symbol details
symbol_detail = agent.get_symbol_details("00700", MarketType.HK)
print(symbol_detail)
```

### Get Orders

```python
# Get all orders
orders = agent.get_orders()

# Get orders by status
from futu_agent import OrderStatusEnum
pending = agent.get_pending_orders()
filled = agent.get_filled_orders()
cancelled = agent.get_cancelled_orders()

# Get specific order
order = agent.get_order_by_id("order_id_123")
```

### Place Order

```python
# Place a buy order
success, result = agent.place_order(
    symbol_code="00700",
    market=MarketType.HK,
    side="BUY",
    quantity=100,
    price=300.0
)

if success:
    print(f"Order placed. ID: {result}")
else:
    print(f"Error: {result}")
```

### Cancel Order

```python
# Cancel an order
success, message = agent.cancel_order(order_id="1234567890")

if success:
    print(f"Success: {message}")
else:
    print(f"Error: {message}")
```

### Account Information

```python
# Get account info
account = agent.get_account_info()
print(f"Cash: {account['cash']}")
print(f"Market Value: {account['market_value']}")
print(f"Total Assets: {account['total_assets']}")

# Get positions
positions = agent.get_positions()
for pos in positions:
    print(f"{pos['symbol']}: {pos['quantity']} @ {pos['price']}")
```

## API Reference

### FutuAgent Class

#### Connection Methods

- `connect() -> bool`: Establish connection to FutuOpenD
- `disconnect() -> bool`: Close connection to FutuOpenD
- `is_connected() -> bool`: Check connection status

#### Symbol Methods

- `get_tradable_symbols(market: Optional[MarketType]) -> Dict[str, List[str]]`: Get tradable symbols
- `get_symbol_details(symbol_code: str, market: MarketType) -> Optional[Dict]`: Get symbol details

#### Order Methods

- `get_orders(status_filter: Optional[OrderStatusEnum]) -> List[Dict]`: Get orders
- `get_order_by_id(order_id: str) -> Optional[Dict]`: Get specific order
- `get_pending_orders() -> List[Dict]`: Get pending orders
- `get_filled_orders() -> List[Dict]`: Get filled orders
- `get_cancelled_orders() -> List[Dict]`: Get cancelled orders
- `place_order(...) -> Tuple[bool, Optional[str]]`: Place new order
- `cancel_order(order_id: str) -> Tuple[bool, Optional[str]]`: Cancel order

#### Account Methods

- `get_account_info() -> Optional[Dict]`: Get account information
- `get_positions() -> List[Dict]`: Get current positions

## Utility Functions

The `utils.py` module provides helper functions organized by category:

- **OrderUtils**: Order formatting and status checking
- **SymbolUtils**: Symbol parsing and validation
- **PositionUtils**: Position calculations
- **TimeUtils**: Timestamp parsing and formatting
- **FilterUtils**: Order and position filtering
- **ValidationUtils**: Parameter validation
- **ReportUtils**: Report generation

Example:
```python
from utils import OrderUtils, PositionUtils

# Check order progress
progress = OrderUtils.calculate_order_progress(order)
print(f"Order is {progress}% filled")

# Calculate position P&L
pnl = PositionUtils.calculate_profit_loss(position)
print(f"Profit/Loss: {pnl}")
```

## Example Script

Run the example script to see all features in action:

```bash
python example_usage.py
```

The example demonstrates:
1. Getting tradable symbols
2. Querying account information
3. Retrieving positions
4. Getting orders by status
5. Order placement (disabled for safety)
6. Order cancellation (disabled for safety)

## Error Handling

All methods include comprehensive error handling:

```python
try:
    agent.connect()
except Exception as e:
    print(f"Connection error: {e}")
```

The agent logs all operations to help with debugging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
agent = FutuAgent()
```

## Important Notes

1. **FutuOpenD Required**: Make sure FutuOpenD is installed and running on the configured host/port
2. **Order Safety**: The example script has order placement/cancellation disabled for safety
3. **Connection Timeout**: All operations require an active connection
4. **Real Trading**: Enable order placement only after thorough testing
5. **Credentials**: Never commit `.env` files with real trading credentials

## Troubleshooting

### Connection Failed
- Check if FutuOpenD is running on the configured host/port
- Verify firewall settings
- Check FUTU_HOST and FUTU_PORT in .env

### Authentication Error
- Verify FutuOpenD credentials
- Check if you're logged in to FutuOpenD

### Order Placement Failed
- Verify sufficient account balance
- Check market hours
- Ensure symbol is tradable

## License

[Add license information]

## Support

For issues or questions, please refer to:
- FutuOpenD Documentation: [Link to docs]
- Example usage: See `example_usage.py`
- Utils documentation: See docstrings in `utils.py`
