import datetime
import threading


class ReminderData:
    def __init__(self):
        self.reminders = []
        self.lock = threading.Lock()  # To ensure thread safety

    def add_reminder(self, chat_id, message, time_str):
        # Parse the time string into a datetime object (assuming 'HHMM' format)
        reminder_time = datetime.datetime.strptime(time_str, '%H%M').replace(
            year=datetime.datetime.now().year,
            month=datetime.datetime.now().month,
            day=datetime.datetime.now().day
        )

        reminder_data = {
            'chat_id': chat_id,
            'message': message,
            'time': reminder_time,
            'fired': False  # To track if the reminder has been fired
        }

        with self.lock:  # Ensure thread safety
            self.reminders.append(reminder_data)

        return reminder_data

    def get_reminders(self):
        with self.lock:
            return self.reminders

    def should_be_fired(self, reminder):
        # Check if the reminder time has passed and it hasn't been fired yet
        return not reminder['fired'] and datetime.datetime.now() >= reminder['time']

    def fire(self, reminder):
        with self.lock:
            reminder['fired'] = True  # Mark the reminder as fired
