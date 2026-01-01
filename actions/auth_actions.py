import time
from core.logger import log_info, log_error, log_warn
from config.config import CONFIG
from core.human_actions import random_delay, type_text, safe_click

def login_to_linkedin(page):
    """
    Checks if logged in, and if not, attempts to log in using configured credentials.
    """
    try:
        log_info("Checking Login Status...", module="AUTH")
        
        # Navigate to a page that redirects if not logged in (e.g., feed)
        if "feed" not in page.url:
            page.goto("https://www.linkedin.com/feed/")
            time.sleep(3)
            
        # Check signs of being logged out
        # 1. URL contains 'login' or 'uas/login'
        # 2. "Sign in" button is visible
        # 3. Feed is not visible
        
        if "login" in page.url or page.locator("input#username").is_visible() or page.locator("input#session_key").is_visible():
            log_warn("Not logged in. Attempting Auto-Login...", module="AUTH")
            
            email = CONFIG["LINKEDIN"]["EMAIL"]
            password = CONFIG["LINKEDIN"]["PASSWORD"]
            
            if not email or not password:
                log_error("Credentials missing in config. Cannot auto-login.", module="AUTH")
                return False
                
            # Handle different login page variants
            
            # Variant 1: Direct form
            username_field = page.locator("input#username")
            if not username_field.is_visible():
                username_field = page.locator("input#session_key") # Classic login page
                
            password_field = page.locator("input#password")
            if not password_field.is_visible():
                password_field = page.locator("input#session_password")
                
            submit_btn = page.locator("button[type='submit']")
            
            if username_field.is_visible() and password_field.is_visible():
                # Type items
                log_info("Filling credentials...", module="AUTH")
                username_field.fill(email)
                random_delay("ACTION")
                password_field.fill(password)
                random_delay("ACTION")
                
                if submit_btn.is_visible():
                    submit_btn.click()
                    log_info("Clicked Sign In.", module="AUTH")
                    time.sleep(5)
                    
                    # Check for 2FA or Challenge or Success
                    if "feed" in page.url or "check/challenge" not in page.url:
                        log_info("Login successful (likely).", module="AUTH")
                        return True
                    else:
                        log_warn("Login submitted but might need 2FA or verification.", module="AUTH")
                        # We cannot automate 2FA easily, so we might just pause or ask user
                        return False
            else:
                 # Maybe we are on the "Join now" page or splash page?
                 # Try clicking "Sign in" header button
                 signin_link = page.locator("a.nav__button-secondary") # Splash page
                 if signin_link.is_visible():
                     signin_link.click()
                     time.sleep(2)
                     return login_to_linkedin(page) # Recurse once
                     
                 log_error("Could not find login fields.", module="AUTH")
                 return False
        else:
            log_info("Already logged in.", module="AUTH")
            return True
            
    except Exception as e:
        log_error(f"Login process failed: {e}", module="AUTH")
        return False
        
def check_session_health(page):
    """
    Checks if session is still valid during execution.
    Returns True if valid, False if needs login.
    """
    if "login" in page.url:
        return False
        
    # Maybe check for specific header element?
    # Global nav is usually present
    if page.locator("#global-nav").is_visible():
        return True
        
    return True # Assume true unless obvious login url
