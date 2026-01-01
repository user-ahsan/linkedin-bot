import random
import time
from config.config import CONFIG
from core.logger import log_info, log_error

def random_delay(action_type="ACTION"):
    """
    Sleeps for a random amount of time based on config.
    action_type can be 'ACTION', 'SHORT_BREAK', 'LONG_BREAK'
    """
    min_delay = 0
    max_delay = 0
    
    delays = CONFIG["DELAYS"]
    
    if action_type == "ACTION":
        min_delay = delays["ACTION_MIN"]
        max_delay = delays["ACTION_MAX"]
    elif action_type == "SHORT_BREAK":
        min_delay = delays["SHORT_BREAK_MIN"]
        max_delay = delays["SHORT_BREAK_MAX"]
    elif action_type == "LONG_BREAK":
        min_delay = delays["LONG_BREAK_MIN"]
        max_delay = delays["LONG_BREAK_MAX"]
        
    delay = random.uniform(min_delay, max_delay)
    log_info(f"Sleeping for {delay:.2f}s ({action_type})", module="HUMAN")
    time.sleep(delay)

def human_scroll(page):
    """
    Scrolls the page in a human-like manner (random small scrolls).
    """
    try:
        current_scroll = 0
        scroll_amount = random.randint(300, 700)
        
        # Scroll in chunks
        while current_scroll < scroll_amount:
            step = random.randint(50, 150)
            page.mouse.wheel(0, step)
            current_scroll += step
            time.sleep(random.uniform(0.1, 0.4))
            
    except Exception as e:
        log_error(f"Scroll failed: {e}")

def safe_click(page, selector, timeout=5000):
    """
    Waits, hovers, and clicks a selector safely.
    """
    try:
        element = page.wait_for_selector(selector, timeout=timeout)
        if element:
            element.hover()
            time.sleep(random.uniform(0.3, 0.7))
            element.click()
            log_info(f"Clicked: {selector}", module="HUMAN")
            return True
        return False
    except Exception as e:
        log_error(f"Click failed for {selector}: {e}")
        return False

def type_text(page, selector, text):
    """
    Types text with random delays between keystrokes.
    """
    try:
        # Focus first
        safe_click(page, selector)
        page.type(selector, text, delay=random.randint(50, 150)) # Playwright type method handles delay
        log_info(f"Typed text into {selector}", module="HUMAN")
        return True
    except Exception as e:
        log_error(f"Typing failed: {e}")
        return False
