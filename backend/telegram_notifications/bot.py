import telegram
import asyncio
from .models import TelegramSettings

# --- Try to import ParseMode from different locations based on version ---
try:
    from telegram.constants import ParseMode
except ImportError:
    try:
        from telegram import ParseMode
    except ImportError:
        # Fallback class if import fails entirely
        class ParseMode:
            HTML = 'HTML'

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

def send_telegram_message(chat_id, text, parse_mode=ParseMode.HTML):
    """
    Sends a text message to a specific Telegram chat.
    Uses the ParseMode constant to ensure HTML is rendered.
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
        # Use asyncio.run() to execute the async function from your sync code
        message = asyncio.run(bot.send_document(
            chat_id=chat_id,
            document=document,
            caption=caption,
            parse_mode=ParseMode.HTML
        ))
        return message
    except telegram.error.BadRequest as e:
        print(f"Telegram BadRequest Error: {e}")
        raise Exception(f"Telegram Error: {e.message}")
    except Exception as e:
        print(f"General Error sending Telegram message: {e}")
        raise Exception(f"An unexpected error occurred: {str(e)}")