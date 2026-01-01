import random
import time
from core.logger import log_info, log_error
from core.human_actions import random_delay, human_scroll, safe_click
from core.rate_limiter import RateLimiter
from core.captcha_detector import CaptchaDetector
# from core.browser import BrowserManager # Passed as arg usually

def run_feed_cycle(page, rate_limiter: RateLimiter, captcha_detector: CaptchaDetector, sheets_client=None):
    """
    Simulates reading the feed and probabilistically liking posts.
    """
    log_info("Starting Feed Engagement Cycle...")
    
    try:
        # 1. Check CAPTCHA
        captcha_detector.check_for_captcha(page)
        
        # 2. Navigate to feed (if not already there)
        if "feed" not in page.url:
            page.goto("https://www.linkedin.com/feed/")
            random_delay("ACTION")
        
        # 3. Scroll a bit
        scrolls = 1 # Reduced for testing
        processed_likes = 0
        
        for _ in range(scrolls):
            captcha_detector.check_for_captcha(page)
            human_scroll(page)
            
            # 4. Probabilistic Like
            # Only if we haven't liked too many in this session
            if processed_likes < 2 and random.random() < 0.3: # 30% chance to try liking a visible post
                if rate_limiter.can_perform("likes"):
                    # Find a like button. 
                    # Selector strategy: Button with aria-label containing "Like" or "React"
                    # Note: LinkedIn selectors are complex. This is best-effort.
                    # A generic selector: 'button[aria-label*="Like"]' might find many.
                    # We need to pick one in view.
                    
                    # For simplicity in this blueprint impl, we try a generic approach
                    # In real usage, would need robust visibility check.
                    
                    try:
                        # Get all like buttons
                        buttons = page.locator('button[aria-label^="React Like"]').all()
                        if buttons:
                            # Pick a random one from the first few
                            btn = buttons[random.randint(0, min(len(buttons)-1, 3))]
                            if btn.is_visible():
                                btn.click()
                                log_info("Liked a post!", module="FEED")
                                rate_limiter.increment("likes")
                                processed_likes += 1
                                
                                if sheets_client:
                                    import datetime
                                    # timestamp, action, target, status, session_id
                                    row = [str(datetime.datetime.now()), "LIKE", "Feed Post", "SUCCESS", "N/A"]
                                    sheets_client.append_interaction(row)

                                random_delay("ACTION")
                    except Exception as e:
                        log_error(f"Like attempt failed: {e}", module="FEED")

            random_delay("SHORT_BREAK")
            
    except Exception as e:
        log_error(f"Feed cycle error: {e}", module="FEED")
