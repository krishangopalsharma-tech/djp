# Path: backend/telegram_notifications/bot.py
import telegram
from .models import TelegramSettings
import asyncio

def get_bot_token():
    """
    Fetches the bot token from the singleton settings.
    """
    try:
        settings = TelegramSettings.objects.get(pk=1)
        return settings.bot_token
    except TelegramSettings.DoesNotExist:
        print("Telegram settings not found. Cannot send message.")
        return None

def send_telegram_message(chat_id, text, parse_mode='HTML'):
    """
    Sends a text message to a specific Telegram chat.
    """
    token = get_bot_token()
    if not token:
        raise Exception("Telegram Bot Token is not configured in settings.")
    if not chat_id:
        raise Exception("Chat ID is not configured for this group.")

    try:
        bot = telegram.Bot(token=token)
        # Use asyncio.run() to execute the async function from your sync code
        asyncio.run(bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode
        ))
        return True
    except telegram.error.BadRequest as e:
        # Common errors: Chat not found, user blocked bot
        print(f"Telegram BadRequest Error: {e}")
        raise Exception(f"Telegram Error: {e.message}")
    except Exception as e:
        print(f"General Error sending Telegram message: {e}")
        raise Exception(f"An unexpected error occurred: {str(e)}")

def send_telegram_document(chat_id, document, caption):
    """
    Sends a document to a specific Telegram chat.
    """
    token = get_bot_token()
    if not token:
        raise Exception("Telegram Bot Token is not configured in settings.")
    if not chat_id:
        raise Exception("Chat ID is not configured for this group.")

    try:
        bot = telegram.Bot(token=token)
        asyncio.run(bot.send_document(
            chat_id=chat_id,
            document=document,
            caption=caption,
            parse_mode='HTML'
        ))
        return True
    except telegram.error.BadRequest as e:
        print(f"Telegram BadRequest Error: {e}")
        raise Exception(f"Telegram Error: {e.message}")
    except Exception as e:
        print(f"General Error sending Telegram message: {e}")
        raise Exception(f"An unexpected error occurred: {str(e)}")