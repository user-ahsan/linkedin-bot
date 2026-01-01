from config.config import CONFIG
from core.state_manager import StateManager
from core.logger import log_info, log_warn

class RateLimiter:
    def __init__(self, state_manager: StateManager):
        self.sm = state_manager
        self.limits = CONFIG["LIMITS"]

    def can_perform(self, action_type):
        """
        action_type: 'likes', 'profile_visits', 'connections' (keys must match state and config)
        """
        if action_type == "likes":
            limit = self.limits["LIKES_PER_DAY"]
            current = self.sm.get_cnt("likes")
            if current < limit:
                return True
        elif action_type == "profile_visits":
            limit = self.limits["PROFILE_VISITS_PER_DAY"]
            current = self.sm.get_cnt("profile_visits")
            if current < limit:
                return True
        elif action_type == "connections":
            limit = self.limits["CONNECTIONS_PER_DAY"]
            current = self.sm.get_cnt("connections")
            if current < limit:
                return True
        
        log_warn(f"Rate limit reached for {action_type} ({self.sm.get_cnt(action_type)}/{limit})")
        return False

    def increment(self, action_type):
        self.sm.increment(action_type)
        current = self.sm.get_cnt(action_type)
        log_info(f"Incremented {action_type}: {current}")
