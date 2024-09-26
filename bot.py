import datetime
import threading
import time
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

# Define a class for managing reminders in memory
class MemoryDataSource:
    def __init__(self):
        self.reminders = []
        self.lock = threading.Lock()  # Ensure thread safety

    def add_reminder(self, chat_id, message, time):
        reminder_data = {
            'chat_id': chat_id,
            'message': message,
            'time': time,
            'fired': False  # To track if the reminder has been fired
        }
        with self.lock:
            self.reminders.append(reminder_data)
        return reminder_data

    def get_reminders(self):
        with self.lock:
            return list(self.reminders)

    def should_be_fired(self, reminder):
        current_time = datetime.datetime.now().strftime("%H%M")
        return current_time >= reminder['time'] and not reminder['fired']

    def fire(self, reminder):
        with self.lock:
            reminder['fired'] = True

# Your bot token
TOKEN = '7455190375:AAF1MTzcgyNiAehObzDWZ1NFEzegLWSWpIs'
INTERVAL = 60

# Define states for conversation handler
ENTER_MESSAGE, ENTER_TIME = range(2)

dataSource = MemoryDataSource()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, trader", reply_markup=add_reminder_button())

def add_reminder_button():
    keyboard = [[KeyboardButton("Add reminder")]]
    return ReplyKeyboardMarkup(keyboard)

async def add_reminder_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please enter your reminder message.")
    return ENTER_MESSAGE

async def enter_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    context.user_data['reminder_message'] = user_message
    await update.message.reply_text("Please enter a time when the bot should remind you (in HHMM format).")
    return ENTER_TIME

async def enter_time_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reminder_time = update.message.text
    reminder_message = context.user_data.get('reminder_message', '')

    try:
        # Validate the time format
        datetime.datetime.strptime(reminder_time, "%H%M")
    except ValueError:
        await update.message.reply_text("Invalid time format. Please enter time in HHMM format.")
        return ENTER_TIME

    message_data = dataSource.add_reminder(update.message.chat_id, reminder_message, reminder_time)

    formatted_message = (
        f"Your reminder has been added:\n"
        f"Message: {message_data.get('message', 'No message found')}\n"
        f"Time: {message_data.get('time', 'No time found')}"
    )

    await update.message.reply_text(formatted_message)
    return ConversationHandler.END

def start_check_reminders_task(application):
    thread = threading.Thread(target=check_reminders, args=(application,))
    thread.daemon = True
    thread.start()

def check_reminders(application):
    while True:
        reminders = dataSource.get_reminders()
        for reminder in reminders:
            if dataSource.should_be_fired(reminder):
                application.bot.send_message(
                    chat_id=reminder['chat_id'],
                    text=f"Reminder: {reminder['message']} at {reminder['time']}"
                )
                dataSource.fire(reminder)
        time.sleep(INTERVAL)

if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()

    start_check_reminders_task(application)

    application.add_handler(CommandHandler("start", start))

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("Add reminder"), add_reminder_handler)],
        states={
            ENTER_MESSAGE: [MessageHandler(filters.ALL, enter_message_handler)],
            ENTER_TIME: [MessageHandler(filters.ALL, enter_time_handler)],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    application.run_polling()
