from core.logger import log_error, log_fatal
from core.state_manager import StateManager
from config.config import CONFIG
# from core.notifier import Notifier # Circular import risk if Notifier uses something else? Notifier should be standalone.

class CaptchaDetector:
    def __init__(self, state_manager: StateManager):
        self.sm = state_manager
        # self.notifier = Notifier() # Initialize later or dependency inject

    def check_for_captcha(self, page):
        """
        Checks for various CAPTCHA signals.
        Returns True if CAPTCHA detected, False otherwise.
        """
        try:
            url = page.url
            if "/checkpoint/" in url or "challenge" in url:
                self.handle_captcha("URL Checkpoint detected")
                return True
            
            # Simple text checks
            # content = page.content() # Expensive? Maybe just check title or specific selector
            # if "Verify you are human" in content: ...
            
            # Check for specific elements if known (iframe with specific captcha ID)
            # This requires knowing LinkedIn's current captcha structure.
            # Using generic safety check.
            
            return False
        except Exception as e:
            log_error(f"Error checking for CAPTCHA: {e}")
            return False

    def handle_captcha(self, reason):
        log_fatal(f"CAPTCHA DETECTED: {reason}")
        self.sm.set_status("BLOCKED_BY_CAPTCHA")
        # Send email if enabled
        if CONFIG["ENABLE_EMAIL_ALERTS"] and CONFIG["EMAIL_ON_CAPTCHA"]:
            # self.notifier.send_alert("CAPTCHA DETECTED", reason)
            pass
        
        raise Exception("CAPTCHA_DETECTED")
