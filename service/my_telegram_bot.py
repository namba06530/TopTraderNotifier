from telegram import Update, ForceReply, bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
import json
import atexit
import os

# Load configuration
telegram_token = os.environ['TELEGRAM_TOKEN']

# Initialize Telegram Bot
updater = Updater(telegram_token, use_context=True)
dispatcher = updater.dispatcher

# Load subscribed chat ids from file (if it exists)
try:
    with open('./subscribed_chat_ids.json', 'r') as f:
        subscribed_chat_ids = set(json.load(f))
except FileNotFoundError:
    subscribed_chat_ids = set()


# Save subscribed chat ids to file on exit
@atexit.register
def save_subscribed_chat_ids():
    with open('./subscribed_chat_ids.json', 'w') as f:
        json.dump(list(subscribed_chat_ids), f)


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Hello {user.first_name}! \nThank you for connecting with the Top Traders Notification Bot.\n\n "
             f"Please note that the bot is currently in its development and testing phase. "
             f"You can start receiving alerts by typing /subscribe. "
             f"To unsubscribe, type /unsubscribe. \nThank you for your patience and happy trading!")


def subscribe(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    if chat_id in subscribed_chat_ids:
        update.message.reply_text("You have already subscribed to TopTraderNotifier!")
    else:
        subscribed_chat_ids.add(chat_id)
        update.message.reply_text("Thank you for subscribing to TopTraderNotifier !\n\n"
                                  "You will now receive notifications of important market events.")


def unsubscribe(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    if chat_id in subscribed_chat_ids:
        subscribed_chat_ids.remove(chat_id)
        update.message.reply_text(
            "You have successfully unsubscribed from TopTraderNotifier. We're sorry to see you go!")
    else:
        update.message.reply_text("You are not currently subscribed to TopTraderNotifier.")


def send_message_to_subscribed_users(context: CallbackContext, message):
    """
    Sends message to all subscribed users
    """
    for chat_id in subscribed_chat_ids:
        context.bot.send_message(chat_id, message)
