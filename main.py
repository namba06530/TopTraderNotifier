import threading
from business.entities.monitor_market import monitor_ma_crossover
from service.my_telegram_bot import dispatcher, CommandHandler, start, subscribe, unsubscribe, updater, subscribed_chat_ids
import talib
from datetime import datetime
import requests
import json

now = datetime.now()

# Set SSL verification
httpClient = requests.Session()
httpClient.verify = False

# Load configuration
with open("./config.json", 'r') as f:
    config = json.load(f)

if __name__ == '__main__':
    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("subscribe", subscribe))
    dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe))

    # Start the Telegram bot
    updater.start_polling()

    # Print the list of subscribed chat IDs
    print('----------------------------------------')
    print("-----TOP TRADER NOTIFIER V0.2_BETA-----")
    print('----------------------------------------')
    print("Bot lancé le: ", now.strftime("%d/%m/%Y %H:%M:%S"))
    print(f"Nombre d'abonné(s):", len(subscribed_chat_ids))

    # List of trading pairs to monitor
    pairs_to_monitor = config['pairs_to_monitor']
    print(f"Nombre de paire(s) monitorée(s):", len(pairs_to_monitor))

    # Unit Time
    interval = "5m"
    # Time to wait for refresh
    # seconds = 60
    print(f"Intervalle de Temps: {interval}")
    print('----------------------------------------')
    print()

    # Initialize TA-Lib
    ta_func = talib.SMA
    ta_ma_args = (100, 130)
    ta_ema_args = (35, 55)

    # Monitor MA 100 130 and EMA 35 55 Crossover
    monitor_thread = threading.Thread(target=monitor_ma_crossover,
                                      args=(
                                          pairs_to_monitor, interval, ta_func, ta_ma_args, ta_ema_args, dispatcher))

    monitor_thread.start()
