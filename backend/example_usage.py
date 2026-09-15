"""
Example usage of FutuAgent
Demonstrates the main features: getting symbols, managing orders, and placing orders
"""

from futu_agent import FutuAgent, MarketType, OrderStatusEnum


def main():
    """Main example function"""

    # Initialize agent
    agent = FutuAgent(host="127.0.0.1", port=11111)

    # Connect to FutuOpenD
    if not agent.connect():
        print("Failed to connect to FutuOpenD. Make sure it's running.")
        return

    print("=" * 60)
    print("FUTU AGENT EXAMPLE")
    print("=" * 60)

    # ========== 1. Get Tradable Symbols ==========
    print("\n1. Getting Tradable Symbols...")
    print("-" * 60)

    # Get all symbols
    all_symbols = agent.get_tradable_symbols()
    print(f"\nHK Symbols ({len(all_symbols.get('HK', []))} total):")
    print(f"  First 10: {all_symbols.get('HK', [])[:10]}")

    print(f"\nUS Symbols ({len(all_symbols.get('US', []))} total):")
    print(f"  First 10: {all_symbols.get('US', [])[:10]}")

    # Get specific market symbols
    hk_symbols = agent.get_tradable_symbols(market=MarketType.HK)
    print(f"\nHK Market Only: {len(hk_symbols.get('HK', []))} symbols")

    us_symbols = agent.get_tradable_symbols(market=MarketType.US)
    print(f"US Market Only: {len(us_symbols.get('US', []))} symbols")

    # Get symbol details
    print("\n\nGetting Symbol Details...")
    hk_symbol_detail = agent.get_symbol_details("00700", MarketType.HK)
    if hk_symbol_detail:
        print(f"HK Symbol 00700: {hk_symbol_detail}")

    us_symbol_detail = agent.get_symbol_details("AAPL", MarketType.US)
    if us_symbol_detail:
        print(f"US Symbol AAPL: {us_symbol_detail}")

    # ========== 2. Get Account Information ==========
    print("\n" + "=" * 60)
    print("2. Getting Account Information...")
    print("-" * 60)

    account_info = agent.get_account_info()
    if account_info:
        print(f"Account Info:")
        for key, value in account_info.items():
            print(f"  {key}: {value}")

    # ========== 3. Get Positions ==========
    print("\n" + "=" * 60)
    print("3. Getting Current Positions...")
    print("-" * 60)

    positions = agent.get_positions()
    print(f"\nTotal Positions: {len(positions)}")
    for pos in positions:
        print(f"\n  Symbol: {pos['symbol']}")
        print(f"    Quantity: {pos['quantity']}")
        print(f"    Available Qty: {pos['available_qty']}")
        print(f"    Price: {pos['price']}")
        print(f"    Market Value: {pos['market_value']}")
        print(f"    Profit/Loss: {pos['profit_loss']} ({pos['profit_loss_ratio']}%)")

    # ========== 4. Get Orders ==========
    print("\n" + "=" * 60)
    print("4. Getting Orders...")
    print("-" * 60)

    # Get all orders
    all_orders = agent.get_orders()
    print(f"\nTotal Orders: {len(all_orders)}")

    for order in all_orders:
        print(f"\n  Order ID: {order['order_id']}")
        print(f"    Symbol: {order['symbol']}")
        print(f"    Side: {order['side']}")
        print(f"    Status: {order['status']}")
        print(f"    Quantity: {order['quantity']}")
        print(f"    Filled: {order['filled_qty']}")
        print(f"    Price: {order['price']}")
        print(f"    Filled Price: {order['filled_price']}")

    # Get pending orders only
    print("\n\nPending Orders:")
    pending_orders = agent.get_pending_orders()
    print(f"Total Pending: {len(pending_orders)}")
    for order in pending_orders:
        print(f"  Order ID: {order['order_id']}, Symbol: {order['symbol']}, Status: {order['status']}")

    # Get filled orders only
    print("\nFilled Orders:")
    filled_orders = agent.get_filled_orders()
    print(f"Total Filled: {len(filled_orders)}")
    for order in filled_orders:
        print(f"  Order ID: {order['order_id']}, Symbol: {order['symbol']}, Status: {order['status']}")

    # Get cancelled orders only
    print("\nCancelled Orders:")
    cancelled_orders = agent.get_cancelled_orders()
    print(f"Total Cancelled: {len(cancelled_orders)}")
    for order in cancelled_orders:
        print(f"  Order ID: {order['order_id']}, Symbol: {order['symbol']}, Status: {order['status']}")

    # ========== 5. Place Order (COMMENTED OUT - UNCOMMENT TO USE) ==========
    print("\n" + "=" * 60)
    print("5. Placing Order (Example - Commented Out)...")
    print("-" * 60)

    print("\nExample code to place order (DISABLED for safety):")
    print("""
    # Uncomment and modify to use:
    success, result = agent.place_order(
        symbol_code='00700',
        market=MarketType.HK,
        side='BUY',
        quantity=100,
        price=300.0
    )
    
    if success:
        print(f"Order placed successfully. Order ID: {result}")
    else:
        print(f"Failed to place order: {result}")
    """)

    # ========== 6. Cancel Order (COMMENTED OUT - UNCOMMENT TO USE) ==========
    print("\n" + "=" * 60)
    print("6. Cancelling Order (Example - Commented Out)...")
    print("-" * 60)

    print("\nExample code to cancel order (DISABLED for safety):")
    print("""
    # Uncomment and modify to use:
    success, message = agent.cancel_order(order_id='1234567890')
    
    if success:
        print(f"Success: {message}")
    else:
        print(f"Error: {message}")
    """)

    # Disconnect
    print("\n" + "=" * 60)
    print("Disconnecting...")
    agent.disconnect()
    print("Done!")


if __name__ == "__main__":
    main()
