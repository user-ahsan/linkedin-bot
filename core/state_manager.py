import json
import os
from datetime import date
from core.logger import log_info, log_error

STATE_DIR = "storage"
STATE_FILE = "local_state.json"
STATE_PATH = os.path.join(STATE_DIR, STATE_FILE)

DEFAULT_STATE = {
    "date": str(date.today()),
    "likes": 0,
    "profile_visits": 0,
    "connections": 0,
    "search_term_index": 0,
    "profile_index": 0,  # Index within the current search results or list
    "status": "RUNNING"  # RUNNING, SLEEPING, BLOCKED_BY_CAPTCHA, STOPPED
}

class StateManager:
    def __init__(self):
        self._ensure_storage_dir()
        self.state = self.load_state()
        self.check_daily_reset()

    def _ensure_storage_dir(self):
        if not os.path.exists(STATE_DIR):
            os.makedirs(STATE_DIR)

    def load_state(self):
        if os.path.exists(STATE_PATH):
            try:
                with open(STATE_PATH, 'r') as f:
                    return json.load(f)
            except Exception as e:
                log_error(f"Failed to load state: {e}. Using default.")
                return DEFAULT_STATE.copy()
        else:
            return DEFAULT_STATE.copy()

    def save_state(self):
        try:
            with open(STATE_PATH, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            log_error(f"Failed to save state: {e}")

    def check_daily_reset(self):
        today_str = str(date.today())
        if self.state.get("date") != today_str:
            log_info(f"New day detected ({today_str}). Resetting counters.")
            self.state["date"] = today_str
            self.state["likes"] = 0
            self.state["profile_visits"] = 0
            self.state["connections"] = 0
            self.save_state()

    def get_cnt(self, key):
        return self.state.get(key, 0)

    def increment(self, key):
        if key in self.state:
            self.state[key] += 1
            self.save_state()
        else:
            log_error(f"Invalid state key increment: {key}")

    def set_status(self, status):
        log_info(f"State transition: {self.state.get('status')} -> {status}")
        self.state["status"] = status
        self.save_state()
    
    def is_blocked(self):
        return self.state.get("status") == "BLOCKED_BY_CAPTCHA"

    def get_var(self, key, default=None):
        return self.state.get(key, default)

    def set_var(self, key, value):
        self.state[key] = value
        self.save_state()
