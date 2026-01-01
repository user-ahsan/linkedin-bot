import datetime
import time
import random
from config.config import CONFIG
from core.logger import log_info, log_warn
from core.human_actions import random_delay

class Scheduler:
    def __init__(self):
        # We read config dynamically or once. 
        # Reading once is fine, but we must handle None.
        pass

    def is_within_active_hours(self):
        start_hour = CONFIG["SCHEDULER"]["START_HOUR"]
        end_hour = CONFIG["SCHEDULER"]["END_HOUR"]

        # Bypass mode: If start is None (active all day)
        if start_hour is None:
            return True

        # Treat 0-0 as 24/7 if user attempts that
        if start_hour == 0 and end_hour == 0:
            return True

        now = datetime.datetime.now()
        current_hour = now.hour
        
        # Handle midnight crossover? e.g. Start 22, End 6
        if start_hour < end_hour:
            return start_hour <= current_hour < end_hour
        else:
            # Crosses midnight: Active if >= start OR < end
            return current_hour >= start_hour or current_hour < end_hour

    def wait_for_active_hours(self):
        """
        Blocks execution until active hours are reached.
        Returns True if proceeding.
        """
        if self.is_within_active_hours():
            return True
            
        start = CONFIG["SCHEDULER"]["START_HOUR"]
        end = CONFIG["SCHEDULER"]["END_HOUR"]
        log_warn(f"Outside active hours ({start}-{end}). Sleeping...", module="SCHEDULER")
        
        while not self.is_within_active_hours():
            time.sleep(60) # Check every minute
            
        log_info("Active hours reached. Resuming...", module="SCHEDULER")
        return True

    def take_random_break(self, break_type="SHORT_BREAK"):
        random_delay(break_type)
