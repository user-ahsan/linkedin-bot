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
    Scrolls the page in a human-like manner (random small scrolls, pauses, and speed variations).
    """
    try:
        current_scroll = 0
        scroll_amount = random.randint(300, 700)
        
        # Scroll in chunks
        while current_scroll < scroll_amount:
            step = random.randint(50, 150)
            page.mouse.wheel(0, step)
            current_scroll += step
            
            # Micro-pause occasionally
            if random.random() < 0.3:
                time.sleep(random.uniform(0.5, 1.2))
            else:
                time.sleep(random.uniform(0.1, 0.4))
            
    except Exception as e:
        log_error(f"Scroll failed: {e}")

def mouse_move_human(page, start_x, start_y, end_x, end_y, steps=25):
    """
    Moves mouse from start to end in a human-like curve (quadratic Bezier).
    """
    try:
        # Random control point for curve
        control_x = random.randint(min(start_x, end_x), max(start_x, end_x))
        control_y = random.randint(min(start_y, end_y), max(start_y, end_y))
        
        # Offset control point to make it a curve
        offset = random.randint(50, 200)
        if random.choice([True, False]):
            control_x += offset
        else:
            control_y += offset
            
        for i in range(steps + 1):
            t = i / steps
            # Quadratic Bezier formula
            x = (1 - t)**2 * start_x + 2 * (1 - t) * t * control_x + t**2 * end_x
            y = (1 - t)**2 * start_y + 2 * (1 - t) * t * control_y + t**2 * end_y
            
            page.mouse.move(x, y)
            time.sleep(random.uniform(0.005, 0.02)) # Fast but variable movement
    except Exception as e:
        log_error(f"Mouse move failed: {e}")

def safe_click(page, selector, timeout=5000):
    """
    Waits, hovers, and clicks a selector safely with human-like movement.
    """
    try:
        element = page.wait_for_selector(selector, timeout=timeout)
        if element:
            # 1. Move mouse to element smoothly
            box = element.bounding_box()
            if box:
                # Random point within the element
                target_x = box["x"] + random.uniform(5, box["width"] - 5)
                target_y = box["y"] + random.uniform(5, box["height"] - 5)
                
                # Move with steps (linear smoothing)
                page.mouse.move(target_x, target_y, steps=random.randint(20, 50))
                
                # 2. Hover and small delay
                element.hover()
                time.sleep(random.uniform(0.3, 0.7))
                
                # 3. Click
                element.click()
                log_info(f"Clicked: {selector}", module="HUMAN")
                return True
            else:
                # Fallback if no box
                element.hover()
                time.sleep(random.uniform(0.3, 0.7))
                element.click()
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
