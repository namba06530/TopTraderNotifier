from datetime import datetime, timedelta
from common.utils import interval_to_seconds


def set_leverage(session, symbol, leverage):
    response = session.set_leverage(symbol=symbol, leverage=leverage)
    return response


def place_order(session, symbol, side, qty, entry_price, stop_loss, tp1, tp2, interval, n=3, leverage=5):
    # Set leverage
    set_leverage(session, symbol, leverage)

    # Calculate order expiry time
    current_time = datetime.now()
    time_to_expiry = interval_to_seconds(interval) * n
    expiry_time = current_time + timedelta(seconds=time_to_expiry)
    expiry_time_str = expiry_time.strftime('%Y-%m-%dT%H:%M:%S')

    # Place the entry order
    entry_order = session.place_active_order(
        symbol=symbol,
        side=side,
        order_type='Limit',
        qty=qty,
        price=entry_price,
        time_in_force='GTT',
        reduce_only=False,
        close_on_trigger=False,
        ext_field1=expiry_time_str
    )

    # Place the stop loss order
    stop_order_side = 'Buy' if side == 'Sell' else 'Sell'
    stop_order = session.place_conditional_order(
        symbol=symbol,
        side=stop_order_side,
        order_type='Market',
        qty=qty,
        stop_px=stop_loss,
        time_in_force='GTC',
        reduce_only=True,
        close_on_trigger=True
    )

    # Place take profit orders (tp1 and tp2)
    tp_orders = []
    for tp in [tp1, tp2]:
        tp_order = session.place_conditional_order(
            symbol=symbol,
            side=stop_order_side,
            order_type='Limit',
            price=tp,
            qty=qty // 2,  # Assuming equal quantities for tp1 and tp2
            time_in_force='GTC',
            reduce_only=True,
            close_on_trigger=True,
            trigger_px=tp
        )
        tp_orders.append(tp_order)

    return entry_order, stop_order, tp_orders


def get_balance_usdt(session):
    balance_data = session.get_wallet_balance(accountType="UNIFIED", coin="USDT")
    coins = balance_data["list"][0]["coin"]

    usdt_balance = 0
    for coin in coins:
        if coin["coin"] == "USDT":
            usdt_balance = float(coin["walletBalance"])
            break

    return usdt_balance


def calculate_order_quantity(session, percentage=50):
    balance = get_balance_usdt(session)
    qty = balance * (percentage / 100)
    return str(int(qty))  # Convert to integer as Bybit requires whole number quantities and return as string
