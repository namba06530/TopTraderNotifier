import threading
import time
import schedule as schedule
from business.entities.monitor_market import monitor_ma_crossover
from service.my_telegram_bot import dispatcher, CommandHandler, start, subscribe, unsubscribe, updater, \
    subscribed_chat_ids
import talib
from datetime import datetime
import requests
import json
from data.binance_api import get_usdt_perpetual_symbols, update_config_file, get_top_volume_symbols


def update_top_pairs():
    top_volume_symbols = get_top_volume_symbols(interval, number_of_candles, top_pairs)
    update_config_file(config_file, top_volume_symbols)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp}: Top {top_pairs} pairs updated")


config_file = "./config.json"
# Load configuration
with open(config_file, 'r') as f:
    config = json.load(f)

now = datetime.now()
interval = "5m"
top_pairs = 100
number_of_candles = 12

# Initialize TA-Lib
ta_func = talib.SMA
ta_ma_args = (100, 130)
ta_ema_args = (35, 55)

# Set SSL verification
httpClient = requests.Session()
httpClient.verify = True

# Load Perpetual USDT pairs from Binance
# binance_pairs = get_usdt_perpetual_symbols()

# Load the top 50 pairs by volume from Binance
top_volume_symbols = get_top_volume_symbols(interval, number_of_candles, top_pairs)

# Update the configuration file
update_config_file(config_file, top_volume_symbols)

# List of trading pairs to monitor
pairs_to_monitor = config['pairs_to_monitor']

if __name__ == '__main__':

    # Schedule the update of the top pairs every hour
    schedule.every(4).hours.do(update_top_pairs)

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("subscribe", subscribe))
    dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe))

    # Start the Telegram bot
    updater.start_polling()

    # Monitor MA 100 130 and EMA 35 55 Crossover
    monitor_thread = threading.Thread(target=monitor_ma_crossover,
                                      args=(
                                          pairs_to_monitor, interval, ta_func, ta_ma_args, ta_ema_args, dispatcher))  # dispatcher

    monitor_thread.start()

    print('----------------------------------------')
    print("-----TOP TRADER NOTIFIER V0.2_BETA------")
    print('----------------------------------------')
    print("Bot lancé le: ", now.strftime("%d/%m/%Y %H:%M:%S"))
    print(f"Nombre d'abonné(s):", len(subscribed_chat_ids))
    print(f"Nombre de paire(s) monitorée(s):", len(pairs_to_monitor))
    print(f"Intervalle de Temps: {interval}")
    print('----------------------------------------')
    print()

    while True:
        schedule.run_pending()
        time.sleep(1)
