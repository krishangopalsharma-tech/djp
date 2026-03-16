from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from supervisors.models import Supervisor
from operations.models import SupervisorMovement
from asgiref.sync import sync_to_async
from django.utils import timezone
from datetime import datetime
import logging

# States
MENU, REGISTER_SELECT, MOVEMENT_LOCATION, MOVEMENT_PURPOSE, LEAVE_START, LEAVE_END, LEAVE_LOOKAFTER_SELECT = range(7)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    # Check if registered
    supervisor = await sync_to_async(lambda: Supervisor.objects.filter(telegram_chat_id=user_id).first())()
    
    if supervisor:
        return await show_menu(update, context, f"Welcome back, {supervisor.name}!")
    else:
        # Fetch all supervisors without telegram_id or allow re-registering?
        # Listing all for simplicity
        supervisors = await sync_to_async(lambda: list(Supervisor.objects.all().values('id', 'name')))()
        
        keyboard = []
        row = []
        for s in supervisors:
            row.append(InlineKeyboardButton(s['name'], callback_data=f"reg_{s['id']}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
            
        await update.message.reply_text(
            "Welcome! Please select your name to register:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return REGISTER_SELECT

async def register_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if not data.startswith("reg_"):
        return REGISTER_SELECT
        
    supervisor_id = data.split("_")[1]
    user_id = str(update.effective_user.id)
    
    # Save mapping
    await sync_to_async(update_supervisor_telegram)(supervisor_id, user_id)
    
    await query.edit_message_text(text="Registration successful!")
    return await show_menu(update, context, "Registration successful!")

def update_supervisor_telegram(sup_id, chat_id):
    Supervisor.objects.filter(id=sup_id).update(telegram_chat_id=chat_id)

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, text):
    keyboard = [['🏃 Enter Movement', '✈️ Enter Leave'], ['❌ Cancel']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    # Handle both callback query (from register) and message (from start/menu)
    if update.callback_query:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)
    return MENU

async def menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == '🏃 Enter Movement':
        await update.message.reply_text("Please enter your current **Location**:", parse_mode='Markdown')
        return MOVEMENT_LOCATION
    elif text == '✈️ Enter leave' or text == '✈️ Enter Leave': # Handle case types
        await update.message.reply_text("Please enter **Start Date** (DD-MM-YYYY):", parse_mode='Markdown')
        return LEAVE_START
    elif text == '❌ Cancel':
        await update.message.reply_text("Operation cancelled.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        await update.message.reply_text("Please select an option from the menu.")
        return MENU

# --- MOVEMENT FLOW ---
async def movement_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mov_loc'] = update.message.text
    await update.message.reply_text("Enter **Purpose/Details**:", parse_mode='Markdown')
    return MOVEMENT_PURPOSE

async def movement_purpose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mov_purp'] = update.message.text
    
    user_id = str(update.effective_user.id)
    location = context.user_data.get('mov_loc')
    purpose = context.user_data.get('mov_purp')
    
    try:
        await sync_to_async(save_movement)(user_id, location, purpose)
        await update.message.reply_text("✅ Movement saved successfully!")
    except Exception as e:
        await update.message.reply_text(f"Error saving movement: {e}")
        
    return await show_menu(update, context, "Main Menu")

def save_movement(telegram_id, location, purpose):
    supervisor = Supervisor.objects.get(telegram_chat_id=telegram_id)
    SupervisorMovement.objects.update_or_create(
        supervisor=supervisor,
        date=timezone.now().date(),
        defaults={
            'location': location,
            'purpose': purpose,
            'on_leave': False
        }
    )

# --- LEAVE FLOW ---
async def leave_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        # Validate date
        datetime.strptime(text, '%d-%m-%Y')
        context.user_data['leave_from'] = text
        await update.message.reply_text("Enter **End Date** (DD-MM-YYYY):", parse_mode='Markdown')
        return LEAVE_END
    except ValueError:
        await update.message.reply_text("Invalid format. Please use DD-MM-YYYY (e.g., 16-12-2025).")
        return LEAVE_START

async def leave_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = str(update.effective_user.id)
    try:
        datetime.strptime(text, '%d-%m-%Y')
        context.user_data['leave_to'] = text
        
        # Determine current supervisor's depot to filter list
        current_sup = await sync_to_async(Supervisor.objects.select_related('depot').get)(telegram_chat_id=user_id)
        
        if not current_sup.depot:
            await update.message.reply_text("You are not assigned to a depot. Cannot select Look After.")
            return await show_menu(update, context, "Main Menu")

        # Show list of supervisors for "Look After" (Same Depot, Exclude Self)
        supervisors = await sync_to_async(lambda: list(
            Supervisor.objects.filter(depot=current_sup.depot).exclude(id=current_sup.id).values('id', 'name')
        ))()
        
        if not supervisors:
            await update.message.reply_text("No other supervisors found in your depot.")
            return await show_menu(update, context, "Main Menu")

        keyboard = []
        row = []
        for s in supervisors:
            # Shorten callback data to fit limit
            row.append(InlineKeyboardButton(s['name'], callback_data=f"la_{s['id']}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
            
        await update.message.reply_text(
            "Select who will **Look After**:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return LEAVE_LOOKAFTER_SELECT
        
    except ValueError:
        await update.message.reply_text("Invalid format. Please use DD-MM-YYYY.")
        return LEAVE_END

async def leave_lookafter_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if not data.startswith("la_"):
        return LEAVE_LOOKAFTER_SELECT
        
    look_after_id = data.split("_")[1]
    
    user_id = str(update.effective_user.id)
    leave_from = context.user_data.get('leave_from')
    leave_to = context.user_data.get('leave_to')
    
    try:
        await sync_to_async(save_leave)(user_id, leave_from, leave_to, look_after_id)
        # Edit message to remove buttons
        await query.edit_message_text(f"✅ Leave saved (Look After: ID {look_after_id})")
        return await show_menu(update, context, "Main Menu")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error saving leave: {e}")
        return await show_menu(update, context, "Main Menu")

def save_leave(telegram_id, start_str, end_str, look_after_id):
    supervisor = Supervisor.objects.get(telegram_chat_id=telegram_id)
    # Parse DD-MM-YYYY
    start_date = datetime.strptime(start_str, '%d-%m-%Y').date()
    end_date = datetime.strptime(end_str, '%d-%m-%Y').date()
    
    # Save to the start_date record
    SupervisorMovement.objects.update_or_create(
        supervisor=supervisor,
        date=start_date,
        defaults={
            'on_leave': True,
            'leave_from': start_date,
            'leave_to': end_date,
            'look_after_id': look_after_id,
            'location': 'N/A', # Clear location if on leave
            'purpose': ''
        }
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Export the handler
def get_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler('menu', start)],
        states={
            REGISTER_SELECT: [CallbackQueryHandler(register_select, pattern='^reg_')],
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_choice)],
            MOVEMENT_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, movement_location)],
            MOVEMENT_PURPOSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, movement_purpose)],
            LEAVE_START: [MessageHandler(filters.TEXT & ~filters.COMMAND, leave_start)],
            LEAVE_END: [MessageHandler(filters.TEXT & ~filters.COMMAND, leave_end)],
            LEAVE_LOOKAFTER_SELECT: [CallbackQueryHandler(leave_lookafter_select, pattern='^la_')],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
