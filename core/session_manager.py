import time
import sys
import os
from actions.auth_actions import login_to_linkedin
from core.browser import BrowserManager
from core.logger import log_info, log_warn, log_error

def ensure_session_validity():
    """
    Launches browser, checks login. 
    If not logged in, pauses for manual user intervention.
    """
    log_info("Initializing Browser for Session Check...", module="SESSION")
    bm = BrowserManager()
    
    # Force headless=False just for this check if possible?
    # BrowserManager reads from config. 
    # To check specifically, we really need to see it if we are doing manual login.
    # But BrowserManager.launch_browser logic is fixed to config.
    # Ideally, we should modify config temporarily or BrowserManager takes an override.
    # For now, we assume config might be headless, but if we need manual login, we need a head.
    # If the user has HEADLESS=True, they can't do manual login easily with this script unless we override it.
    
    # Quick dirty override or we just rely on the user having set it?
    # Actually, let's just launch it. If headless, and login fails, we warn them.
    # Better: modify BrowserManager to accept headless override? 
    # Or just modify CONFIG in memory before launching?
    
    from config.config import CONFIG
    original_headless = CONFIG["BROWSER"]["HEADLESS"]
    
    # Force Headed for this specific interaction script
    CONFIG["BROWSER"]["HEADLESS"] = False 
    
    try:
        page = bm.launch_browser()
        
        # 1. Check Login
        is_logged_in = login_to_linkedin(page)
        
        if is_logged_in:
            log_info("✅ Session is valid! You are logged in.", module="SESSION")
            time.sleep(2)
            return True
        else:
            log_warn("⚠️ Not logged in or 2FA required.", module="SESSION")
            print("\n" + "!"*60)
            print("Action Required: Please log in manually in the browser window.")
            print("Navigate to https://www.linkedin.com/feed/ if not there.")
            print("Perform 2FA if requested.")
            print("!"*60 + "\n")
            
            # Wait loop
            while True:
                user_input = input(">> Press ENTER once you have successfully logged in (or type 'q' to quit): ")
                if user_input.lower() == 'q':
                    return False
                
                log_info("Re-checking session...", module="SESSION")
                if "feed" not in page.url:
                    page.goto("https://www.linkedin.com/feed/")
                    time.sleep(3)
                
                # Simple check again
                if "login" not in page.url and page.locator("#global-nav").is_visible():
                    log_info("✅ Login verified!", module="SESSION")
                    return True
                else:
                    log_warn("❌ Still not detected as logged in. Try again.", module="SESSION")

    except Exception as e:
        log_error(f"Session check failed: {e}", module="SESSION")
        return False
    finally:
        # If we just wanted to check/login, we can close.
        # But if this is called by main.py, we might want to keep it open?
        # BrowserManager stores the instance.
        bm.close_browser()

if __name__ == "__main__":
    ensure_session_validity()
