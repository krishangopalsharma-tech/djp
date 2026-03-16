import os
import django
from django.core.management.base import BaseCommand
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from telegram_notifications.models import TelegramSettings, TelegramGroup
from failures.models import Failure, FailureAttachment
from failures.utils import format_failure_message
from telegram_notifications.bot import get_bot_token, send_telegram_message
from asgiref.sync import sync_to_async
from django.utils import timezone
from django.core.files.base import ContentFile

class Command(BaseCommand):
    help = 'Runs the Telegram Bot for interactive notifications'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Telegram Bot...'))
        
        token = get_bot_token()
        if not token:
            self.stdout.write(self.style.ERROR('Bot token not found in settings.'))
            return

        application = Application.builder().token(token).build()

        # Handlers
        from .conversations import get_conversation_handler
        application.add_handler(get_conversation_handler())

        application.add_handler(CallbackQueryHandler(self.button_handler))
        application.add_handler(MessageHandler(filters.Document.ALL & filters.REPLY, self.file_handler))
        application.add_handler(MessageHandler(filters.TEXT & filters.REPLY, self.text_handler))

        # Run the bot
        # We need to run a background task for heartbeat alongside polling.
        # Since run_polling blocks, we can't easily run a loop in handle().
        # Instead, we'll add a job to the JobQueue if available, or just run a simple async loop via create_task if we can access the loop.
        # But Application.run_polling manages the loop.
        
        # Better approach: Add a JobQueue job if we had extensions installed, but standard python-telegram-bot has JobQueue.
        # Let's check imports. We can use application.job_queue.run_repeating if JobQueue is enabled.
        # Default ApplicationBuilder builds a JobQueue unless disabled.
        
        if application.job_queue:
            self.stdout.write(self.style.WARNING('JobQueue ignored. Using manual asyncio loop.'))
        
        # Start manual heartbeat loop
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Post-init hook to start background task
        async def post_init(app):
            asyncio.create_task(self.heartbeat_loop())
            self.stdout.write(self.style.SUCCESS('Manual heartbeat loop started.'))
        
        application.post_init = post_init

        # Explicitly run loop
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    async def heartbeat_loop(self):
        import asyncio
        while True:
            await self.send_heartbeat(None)
            await asyncio.sleep(30)

    async def send_heartbeat(self, context: ContextTypes.DEFAULT_TYPE):
        self.stdout.write(f"Executing heartbeat at {timezone.now()}")
        try:
            # Update the singleton settings object
            await sync_to_async(self._update_heartbeat)()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Heartbeat error: {e}"))

    def _update_heartbeat(self):
        settings = TelegramSettings.objects.first()
        if settings:
            settings.bot_last_heartbeat = timezone.now()
            settings.save(update_fields=['bot_last_heartbeat'])
        else:
             print("No TelegramSettings found to update heartbeat.")

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        try:
            await query.answer()
        except Exception:
            pass # Ignore errors answering old queries

        data = query.data
        action, fail_id = data.split('_', 1)

        try:
            failure = await sync_to_async(Failure.objects.get)(fail_id=fail_id)
            
            if action == 'ack':
                failure.current_status = 'In Progress'
                await sync_to_async(failure.save)()
                
                # Update message
                new_text = query.message.text_html + "\n\n✅ <b>Acknowledged</b>"
                
                # New keyboard: Resolve + Upload (Remove Ack)
                new_keyboard = [
                    [InlineKeyboardButton("Resolve", callback_data=f"resolve_{fail_id}")],
                    [InlineKeyboardButton("Upload File", callback_data=f"upload_{fail_id}")]
                ]
                reply_markup = InlineKeyboardMarkup(new_keyboard)
                
                await query.edit_message_text(text=new_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
                await context.bot.send_message(chat_id=query.message.chat_id, text=f"Failure {fail_id} marked as In Progress.")

            elif action == 'resolve':
                # Force Reply to prompt for resolution notes
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=f"Please reply to this message with the resolution notes for Failure #{fail_id}",
                    reply_markup=ForceReply(selective=True)
                )

            elif action == 'upload':
                # Force Reply to prompt upload
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=f"Please reply to this message with the file for Failure #{fail_id}",
                    reply_markup=ForceReply(selective=True)
                )

        except Failure.DoesNotExist:
            await context.bot.send_message(chat_id=query.message.chat_id, text="Failure not found.")
        except Exception as e:
            print(f"Error in button_handler: {e}")
            await context.bot.send_message(chat_id=query.message.chat_id, text=f"Error: {str(e)}")

    async def file_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.reply_to_message:
            return

        reply_text = update.message.reply_to_message.text
        if "Failure #" not in reply_text:
            return

        try:
            # Extract fail_id from "Please reply ... for Failure #<id>"
            fail_id = reply_text.split('#')[1].strip()
            failure = await sync_to_async(Failure.objects.get)(fail_id=fail_id)

            document = update.message.document
            file_id = document.file_id
            file_name = document.file_name
            
            # Download file from Telegram
            new_file = await context.bot.get_file(file_id)
            file_content = await new_file.download_as_bytearray()

            # Save to FailureAttachment
            # We need to wrap this in sync_to_async because it touches the DB and FileSystem
            await sync_to_async(self.save_attachment)(failure, file_name, file_content, file_id, update.message.message_id)

            await update.message.reply_text(f"File '{file_name}' uploaded successfully for Failure {fail_id}.")

        except Exception as e:
            print(f"Error in file_handler: {e}")
            await update.message.reply_text(f"Upload failed: {str(e)}")

    def save_attachment(self, failure, filename, content, telegram_file_id, telegram_message_id):
        attachment = FailureAttachment(
            failure=failure,
            telegram_file_id=telegram_file_id,
            telegram_message_id=telegram_message_id,
            description="Uploaded via Telegram Bot"
        )
        # Save the file content to the FileField
        attachment.file.save(filename, ContentFile(content), save=True)

    async def text_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.reply_to_message:
            return

        reply_text = update.message.reply_to_message.text
        if "resolution notes for Failure #" not in reply_text:
            return

        try:
            # Extract fail_id from "Please reply ... for Failure #<id>"
            fail_id = reply_text.split('#')[1].strip()
            failure = await sync_to_async(Failure.objects.get)(fail_id=fail_id)
            
            # Update Failure
            failure.current_status = 'Resolved'
            failure.resolved_at = timezone.now()
            failure.remark_right = update.message.text
            await sync_to_async(failure.save)()

            # 1. Reply to Supervisor
            await update.message.reply_text(f"Failure {fail_id} marked as Resolved.")
            
            # 2. Notify Alerts Group
            try:
                alerts_group = await sync_to_async(TelegramGroup.objects.get)(key='alerts')
                if alerts_group.chat_id:
                    # Fetch failure again with related objects to avoid async DB access error during formatting
                    failure_full = await sync_to_async(
                        lambda: Failure.objects.select_related('circuit', 'station', 'section', 'sub_section', 'assigned_to').get(fail_id=fail_id)
                    )()
                    
                    # Format message using shared utility (now safe)
                    message = format_failure_message(failure_full)
                    
                    # Send to alerts group
                    await context.bot.send_message(
                        chat_id=alerts_group.chat_id,
                        text=message,
                        parse_mode=ParseMode.HTML
                    )
            except TelegramGroup.DoesNotExist:
                print("Alerts group not found.")
            except Exception as e:
                print(f"Error sending to alerts group: {e}")

        except Exception as e:
            print(f"Error in text_handler: {e}")
            await update.message.reply_text(f"Error: {str(e)}")
