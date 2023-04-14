import uuid


def create_trade_id():
    # Générer un identifiant unique pour chaque trade
    return str(uuid.uuid4())


def create_new_trade(pair, signal_type):
    trade_id = create_trade_id()
    trade = {
        'id': trade_id,
        'pair': pair,
        'signal_type': signal_type,
        'status': 'open',
        'events': []
    }
    trades[trade_id] = trade
    return trade_id


def update_trade(trade_id, event):
    global trades
    if trade_id in trades:
        trades[trade_id]['events'].append(event)


def calculate_trade_stats():
    global trades

    losing_trades = 0
    break_even_trades = 0
    winning_trades = 0

    for trade_id, trade in trades.items():
        events = trade['events']

        if 'stop_loss' in events:
            losing_trades += 1
        elif 'tp1' in events and 'stop_loss_after_tp1' in events:
            break_even_trades += 1
        elif 'tp1' in events and 'tp2' in events:
            winning_trades += 1

    return {
        'losing_trades': losing_trades,
        'break_even_trades': break_even_trades,
        'winning_trades': winning_trades
    }


def check_trade_events():
    global trades

    for trade_id, trade in trades.items():
        if not trade.get('is_open'):
            continue

        pair = trade['pair']
        signal_type = trade['signal_type']
        entry_price = trade['entry_price']
        stop_loss = trade['stop_loss']
        tp1 = trade['tp1']
        tp2 = trade['tp2']

        # Get the current market price
        current_price = get_current_price(pair)

        # Check if the entry_price is touched
        if not trade.get('entry_price_touched'):
            if signal_type == 'buy' and current_price >= entry_price:
                trade['entry_price_touched'] = True
            elif signal_type == 'sell' and current_price <= entry_price:
                trade['entry_price_touched'] = True

        # Check if the stop_loss is touched
        if trade.get('entry_price_touched') and not trade.get('stop_loss_touched'):
            if signal_type == 'buy' and current_price <= stop_loss:
                trade['stop_loss_touched'] = True
                trade['is_open'] = False
            elif signal_type == 'sell' and current_price >= stop_loss:
                trade['stop_loss_touched'] = True
                trade['is_open'] = False

        # Check if the tp1 is touched
        if trade.get('entry_price_touched') and not trade.get('tp1_touched'):
            if signal_type == 'buy' and current_price >= tp1:
                trade['tp1_touched'] = True
            elif signal_type == 'sell' and current_price <= tp1:
                trade['tp1_touched'] = True

        # Check if the tp2 is touched
        if trade.get('entry_price_touched') and trade.get('tp1_touched') and not trade.get('tp2_touched'):
            if signal_type == 'buy' and current_price >= tp2:
                trade['tp2_touched'] = True
                trade['is_open'] = False
            elif signal_type == 'sell' and current_price <= tp2:
                trade['tp2_touched'] = True
                trade['is_open'] = False
