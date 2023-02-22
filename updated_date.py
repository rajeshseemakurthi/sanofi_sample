import time
from datetime import date,datetime


class Current_things:
    def current_date(self):
        return (date.today())
    
    def current_time(self):
        return (datetime.now().strftime("%H:%M:%S"))
