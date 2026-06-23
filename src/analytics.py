import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

@dataclass
class Event:
    type: str
    timestamp: datetime

class Analytics:
    def __init__(self):
        self.events = []

    def capture_event(self, event_type):
        event = Event(event_type, datetime.now())
        self.events.append(event)

    def get_daily_active_users(self):
        daily_users = defaultdict(int)
        for event in self.events:
            date = event.timestamp.date()
            daily_users[date] += 1
        return daily_users

    def get_conversion_rates(self):
        conversion_rates = defaultdict(int)
        for event in self.events:
            if event.type == 'conversion':
                date = event.timestamp.date()
                conversion_rates[date] += 1
        return conversion_rates

    def get_dashboard_data(self):
        daily_users = self.get_daily_active_users()
        conversion_rates = self.get_conversion_rates()
        dashboard_data = {
            'daily_active_users': dict(daily_users),
            'conversion_rates': dict(conversion_rates)
        }
        return dashboard_data
