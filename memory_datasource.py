
from message_data import ReminderData
class MemoryDataSource:
    def __init__(self):
        # Initialize an empty dictionary to store reminders
        self.reminders = {}

    def add_reminder(self, chat_id, message, time):
        # Add the reminder to the dictionary
        if chat_id not in self.reminders:
            self.reminders[chat_id] = []
        self.reminders[chat_id].append({
            'message': message,
            'time': time
        })
        return {
            'chat_id': chat_id,
            'message': message,
            'time': time
        }
