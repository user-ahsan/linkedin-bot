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
        # 1. Click Connect using Robust Fallback Strategy
        connect_btn = _find_connect_button(page)
        
        if not connect_btn:
             # Check for "More" button -> "Connect"
             # "More" is usually an accessible button with name "More actions" or similar
             more_btn = page.get_by_role("button", name="More actions").first
             if not more_btn.is_visible():
                 more_btn = page.locator("button[aria-label='More actions']").first
             if not more_btn.is_visible():
                 more_btn = page.locator("button").filter(has_text="More").first
                 
             if more_btn.is_visible():
                 more_btn.click()
                 random_delay("ACTION")
                 # Look for Connect in dropdown
                 # Dropdown items often have role="button" or are inside a list
                 connect_in_more = _find_connect_button_in_menu(page)
                 
                 if connect_in_more:
                     connect_in_more.click()
                 else:
                     log_info("Connect option not found in More menu.", module="CONNECT")
                     return False
             else:
                 log_info("Connect button not found (Primary or More)", module="CONNECT")
                 return False
        else:
             connect_btn.click()

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

def _find_connect_button(container):
    """
    Finds the Connect button using accessibility > text fallback chain.
    """
    # 1. Role + Name (Best)
    # Note: 'Connect' is the ideal name. Sometimes 'Connect with [Name]'
    btn = container.get_by_role("button", name=re.compile(r"^Connect", re.IGNORECASE)).first
    if btn.is_visible() and "Connect" in btn.inner_text(): 
        return btn

    # 2. Aria Label
    btn = container.locator("button[aria-label^='Connect']").first
    if btn.is_visible(): return btn

    # 3. Text content (Fallback)
    # Exclude "Connected", "Disconnect"
    btn = container.locator("button").filter(has_text=re.compile(r"^Connect(?!ed|ing)", re.IGNORECASE)).first
    if btn.is_visible(): return btn
    
    return None

def _find_connect_button_in_menu(page):
    """
    Finds connect button specifically in the open dropdown menu.
    """
    # Menu items often have role="button" inside a role="menu" or similar container
    # We search somewhat globally but prioritizing visible elements
    
    # 1. Text with loose match in commonly used dropdown item tags
    # We want to match "Connect" but avoid "Remove Connection"
    candidates = page.locator("div[role='button'], li, span").filter(has_text=re.compile(r"^Connect(?!ed|ing)", re.IGNORECASE)).all()
    for c in candidates:
        if c.is_visible(): return c
        
    return None
