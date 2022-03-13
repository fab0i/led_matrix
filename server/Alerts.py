import random
import time

class BaseAlert:
    def __init__(self, name, stop, soon, date_start, display, display_info, type="base", id=None):
        self.job = "alert"
        self.date_created = time.time()
        self.id = id if id else random.randint(1, 9999999)

        self.name = name
        self.stop = stop
        self.type = type
        self.soon = soon
        self.date_start = date_start
        self.display = display
        self.display_info = display_info
        self.pid = None

    def to_dict(self):
        info = {
            "id": self.id,
            "name": self.name,
            "job": self.job,
            "type": self.type,
            "stop": self.stop,
            "date_created": self.date_created,
            "date_start": self.date_start,
            "soon": self.soon,
            "display": self.display,
            "display_info": self.display_info,
            "pid": self.pid
        }
        return info

class NotificationAlert(BaseAlert):
    def __init__(self, name, stop, soon, date_start, display, display_info):
        BaseAlert.__init__(self, name, stop, soon, date_start, display, display_info, type="notification")

class CalendarAlert(BaseAlert):
    def __init__(self, name, stop, soon, date_start, display, display_info, calendar_id):
        BaseAlert.__init__(self, name, stop, soon, date_start, display, display_info, type="calendar", id=calendar_id)

