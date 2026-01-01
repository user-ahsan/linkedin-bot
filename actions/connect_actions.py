from core.logger import log_info, log_error
from core.human_actions import random_delay, safe_click
from core.rate_limiter import RateLimiter
import re

def send_connection_request(page, note, rate_limiter: RateLimiter):
    """
    Sends connection request, optionally with a note.
    """
    if not rate_limiter.can_perform("connections"):
         log_info("Rate limit reached for connections. Skipping.", module="CONNECT")
         return False

    try:
        # 1. Click Connect
        # Try finding the Connect button. It might be:
        # - Primary action "Connect"
        # - Inside "More" dropdown
        
        # Primary "Connect" button logic
        connect_btn = page.locator('button').filter(has_text=re.compile(r"^Connect$", re.IGNORECASE))
        
        if not connect_btn.first.is_visible():
             # Check for "More" button -> "Connect"
             more_btn = page.locator('button').filter(has_text="More")
             if more_btn.first.is_visible():
                 more_btn.first.click()
                 random_delay("ACTION")
                 # Look for Connect in dropdown
                 # Broader selector with whitespace tolerance
                 connect_in_more = page.locator('div[role="button"], span, li, div').filter(has_text=re.compile(r"^\s*Connect\s*$", re.IGNORECASE))
                 if connect_in_more.first.is_visible():
                     connect_in_more.first.click()
                     connect_btn = connect_in_more # Found it
                 else:
                     log_info("Connect option not found in More menu. Dumping HTML...", module="CONNECT")
                     try:
                         with open("debug_profile_more_menu.html", "w", encoding="utf-8") as f:
                             f.write(page.content())
                     except: pass
                     return False
             else:
                 log_info("Connect button not found", module="CONNECT")
                 return False
        else:
             connect_btn.first.click()

        random_delay("ACTION")
        
        # 2. Handle "Add a note" modal
        # Wait for modal to appear
        try:
            page.wait_for_selector("div.artdeco-modal", timeout=5000)
        except:
            pass # Maybe no modal?

        # Check for "Send without a note" or "Add a note"
        add_note_btn = page.locator('button[aria-label="Add a note"]')
        send_no_note_btn = page.locator('button[aria-label="Send without a note"]')
        
        # Fallback selectors
        if not add_note_btn.is_visible():
            add_note_btn = page.locator('button').filter(has_text="Add a note")
        if not send_no_note_btn.is_visible():
            send_no_note_btn = page.locator('button').filter(has_text="Send without a note")

        # DECISION: Note or No Note?
        if note and add_note_btn.is_visible():
            log_info("Sending with Smart Note...", module="CONNECT")
            add_note_btn.first.click()
            random_delay("ACTION")
            
            # Type note
            text_area = page.locator("textarea[name='message']")
            if not text_area.is_visible():
                 text_area = page.locator("textarea")
            
            text_area.fill(note)
            random_delay("ACTION")
            
            # Send
            send_btn = page.locator('button[aria-label="Send invitation"]')
            if not send_btn.is_visible():
                send_btn = page.locator('button').filter(has_text="Send")
                
            if send_btn.first.is_visible():
                send_btn.first.click()
                log_info("Connection request sent with note.", module="CONNECT")
                rate_limiter.increment("connections")
                
        elif send_no_note_btn.is_visible():
            log_info("Sending WITHOUT note (Config/Key missing or intended).", module="CONNECT")
            send_no_note_btn.first.click()
            random_delay("ACTION")
            rate_limiter.increment("connections")
            
        else:
            # Maybe just "Send"? (Rare case)
            send_generic = page.locator('button').filter(has_text="Send")
            if send_generic.first.is_visible():
                 send_generic.first.click()
                 log_info("Connection request sent (Generic Send).", module="CONNECT")
                 rate_limiter.increment("connections")
            else:
                 log_info("Could not find Send button in modal.", module="CONNECT")
                 return False

        # 3. Handle "Your invitation is sent" / "Add experience" Popup
        random_delay("SHORT_BREAK") # Wait for popup to settle
        
        close_icon = page.locator('button[aria-label="Dismiss"]')
        if not close_icon.is_visible():
             close_icon = page.locator('button[aria-label="Close"]')
             
        if close_icon.first.is_visible():
            log_info("Closing success popup...", module="CONNECT")
            close_icon.first.click()
        else:
            # Check for specific "Got it" or similar if UI changes
            pass

        return True
    
    except Exception as e:
        log_error(f"Connection failed: {e}", module="CONNECT")
        return False
