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

def human_jitter(page):
    """
    Simulates small, random nervous mouse movements (jitter) simulation.
    Useful for 'idle' times.
    """
    try:
        # Get current mouse position (not directly available in pure playwright without tracking, 
        # so we just move relative to a guess or small offsets if we don't know).
        # Since we can't get current pos easily, we'll just move to a random point nearby 
        # or just do a very small move from "center-ish" if we tracked it, 
        # but Playwright doesn't expose strict "current" props easily. 
        # Instead, we will making small moves in a loop.
        
        # NOTE: A better approach is imagining we are 'reading' and moving mouse slightly.
        width = page.viewport_size['width']
        height = page.viewport_size['height']
        
        start_x = random.randint(int(width * 0.2), int(width * 0.8))
        start_y = random.randint(int(height * 0.2), int(height * 0.8))
        
        for _ in range(random.randint(2, 5)):
            offset_x = random.randint(-15, 15)
            offset_y = random.randint(-15, 15)
            page.mouse.move(start_x + offset_x, start_y + offset_y, steps=random.randint(3, 10))
            time.sleep(random.uniform(0.1, 0.3))
            
    except Exception as e:
        # Non-critical 
        pass

def human_scroll(page):
    """
    Scrolls the page in a human-like manner (random small scrolls, reading pauses, reversals, and speed variations).
    """
    try:
        current_scroll = 0
        scroll_amount = random.randint(300, 700)
        
        # Scroll in chunks
        while current_scroll < scroll_amount:
            step = random.randint(50, 150)
            page.mouse.wheel(0, step)
            current_scroll += step
            
            # 1. Micro-pause (reading a line)
            if random.random() < 0.4:
                time.sleep(random.uniform(0.5, 1.5))
            
            # 2. Reading Pause (longer stop)
            if random.random() < 0.1:
                # User stops to read something interesting
                log_info("Simulating reading pause...", module="HUMAN")
                time.sleep(random.uniform(2.0, 4.5))
                # Maybe wiggle mouse while reading
                if random.random() < 0.5:
                    human_jitter(page)

            # 3. Occasional small scroll UP (re-reading)
            if random.random() < 0.05:
                # Scroll up slightly
                up_step = random.randint(20, 50)
                page.mouse.wheel(0, -up_step)
                time.sleep(random.uniform(0.5, 1.0))
                # Then continue down
                page.mouse.wheel(0, up_step) 

            # Normal erratic timing
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
                
                # Optional: Jitter after click (indecision or checking result)
                if random.random() < 0.2:
                    human_jitter(page)
                    
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
    Types text with random delays between keystrokes and occasional 'thinking' pauses.
    """
    try:
        # Focus first
        safe_click(page, selector)
        
        # Type character by character manually for maximum control
        for char in text:
            page.keyboard.type(char, delay=random.randint(30, 100)) # Base fast typing
            
            # Occasional pause (thinking)
            if random.random() < 0.05:
                time.sleep(random.uniform(0.2, 0.8))
                
            # Occasional longer pause (sentence break)
            if char in ['.', ',', '!', '?']:
                time.sleep(random.uniform(0.3, 1.0))
                
        log_info(f"Typed text into {selector}", module="HUMAN")
        return True
    except Exception as e:
        log_error(f"Typing failed: {e}")
        return False
