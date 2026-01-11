import time
import sys
import os
import random
import re
import msvcrt

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import CONFIG
from core.logger import log_info, log_error, log_fatal, log_warn
from core.state_manager import StateManager
from core.browser import BrowserManager
from core.scheduler import Scheduler
from core.rate_limiter import RateLimiter
from core.captcha_detector import CaptchaDetector
from core.notifier import Notifier
from core.human_actions import human_scroll
from storage.sheets_client import SheetsClient

from actions.feed_actions import run_feed_cycle
from actions.search_people import perform_search
from actions.profile_actions import visit_profile, extract_profile_data
from actions.note_generator import generate_note
from actions.connect_actions import send_connection_request
from actions.auth_actions import login_to_linkedin, check_session_health

def check_keyboard_input():
    if msvcrt.kbhit():
        key = msvcrt.getch().decode('utf-8').lower()
        if key == 's':
            log_info("Command 's' received: Stopping/Skipping...", module="INPUT")
            return 's'
        elif key == 'q':
            log_info("Command 'q' received: Quitting to menu...", module="INPUT")
            return 'q'
    return None

def interruptible_sleep(seconds):
    """
    Sleeps for the given duration but checks for keyboard input every 0.1s.
    Raises KeyboardInterrupt if 'q' is pressed.
    Returns 's' if 's' is pressed, otherwise None.
    """
    end_time = time.time() + seconds
    while time.time() < end_time:
        cmd = check_keyboard_input()
        if cmd == 'q':
            raise KeyboardInterrupt("Quit command received during sleep")
        if cmd == 's':
            return 's'
        time.sleep(0.1)
    return None

def main():
    log_info("BOOT: LinkedIn Autonomous Agent Starting...")
    log_info("Commands: Press 's' to stop/skip current action, 'q' to quit to menu.")
    
    # Initialize Core Systems
    state_manager = StateManager()
    scheduler = Scheduler()
    rate_limiter = RateLimiter(state_manager)
    captcha_detector = CaptchaDetector(state_manager)
    notifier = Notifier()
    sheets_client = SheetsClient()
    browser_manager = BrowserManager()
    
    try:
        # Check Scheduler on boot
        if not scheduler.wait_for_active_hours():
            log_info("Outside active hours. Waiting loop started inside wait_for_active_hours or exited.")
            pass

        # Launch Browser
        page = browser_manager.launch_browser()
        
        # 0. Auto-Login Check
        if not login_to_linkedin(page):
            log_fatal("Login failed or requires manual 2FA. Stopping.")
            return

        # Main Automation Loop
        while True:
            cmd = check_keyboard_input()
            if cmd == 'q':
                break
            
            # Check validity
            if not check_session_health(page):
                log_warn("Session invalid. Re-attempting login...")
                if not login_to_linkedin(page):
                    log_fatal("Re-login failed.")
                    break
            # 1. Check Active Hours
            if not scheduler.is_within_active_hours():
                log_info("Active hours ended. Sleeping/Exiting...")
                # Replace long sleep
                if interruptible_sleep(600) == 'q': break
                continue
                
            # 2. Daily Reset Check
            state_manager.check_daily_reset()
            
            # 3. Check Safety
            if state_manager.is_blocked():
                log_fatal("System is BLOCKED by CAPTCHA. Manual intervention required.")
                notifier.send_alert("System Blocked", "Captcha detected. System stopped.")
                break
                
            # 4. Feed Engagement (The "Human" distraction)
            try:
                # We can't easily interrupt inside run_feed_cycle without modifying it, 
                # but it should be fast or have its own sleeps. 
                # For now we assume feed cycle is atomic enough.
                run_feed_cycle(page, rate_limiter, captcha_detector, sheets_client)
            except Exception as e:
                log_error(f"Feed cycle error: {e}")

            # 5. Network Building (The "Goal")
            # Load search terms
            try:
                with open("inputs/searchpeople.txt", "r") as f:
                    keywords = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                keywords = []
                log_warn("inputs/searchpeople.txt not found.")
            
            if keywords:
                # Pick one keyword (round robin or random?)
                idx = state_manager.get_var("search_term_index", 0)
                if idx >= len(keywords):
                    idx = 0
                
                keyword = keywords[idx]
                log_info(f"Starting Search Cycle for: {keyword}")
                
                if sheets_client:
                     import datetime
                     row = [str(datetime.datetime.now()), "SEARCH", keyword, "STARTED", "N/A"]
                     sheets_client.append_interaction(row)
                
                # PAGINATION LOOP
                for page_num in range(1, 101):
                    # Check Input
                    cmd = check_keyboard_input()
                    if cmd == 's':
                        log_info("Skipping search for this keyword...", module="INPUT")
                        break
                    if cmd == 'q':
                        raise KeyboardInterrupt("Quit command received")

                    log_info(f"Processing Page {page_num} for keyword: {keyword}", module="MAIN")
                    
                    if page_num == 1:
                        scroll_loops = CONFIG["SEARCH_SETTINGS"].get("SCROLL_LOOPS", 2)
                        success = perform_search(page, keyword, captcha_detector, scroll_loops)
                        if not success:
                            break 
                    else:
                        current_url = page.url
                        if "linkedin.com/search/results" not in current_url:
                            log_warn("Lost search context, aborting pagination.", module="MAIN")
                            break
                            
                        if "page=" in current_url:
                           new_url = re.sub(r"page=\d+", f"page={page_num}", current_url)
                        else:
                           new_url = current_url + f"&page={page_num}"
                        
                        log_info(f"Navigating to page {page_num}: {new_url}", module="MAIN")
                        page.goto(new_url)
                        
                        # Interruptible Sleep for loading
                        if interruptible_sleep(random.randint(5, 8)) == 'q': raise KeyboardInterrupt("Quit")
                        
                        captcha_detector.check_for_captcha(page)
                        human_scroll(page)
                    
                    # Process Results on Current Page
                    candidates = []
                    try:
                        # Wait for results
                        try:
                            page.wait_for_selector("ul.reusable-search__entity-result-list, .search-results-container, div.entity-result, a[href*='/in/']", timeout=15000)
                        except:
                            log_warn("Standard selectors timed out.", module="MAIN")
                        
                        profile_links_count = page.locator("a[href*='/in/']").count()
                        if profile_links_count == 0:
                             log_warn(f"No profile links found on page {page_num}.", module="MAIN")
                             break
                             
                        # SCAN STEP
                        results = page.locator("ul.reusable-search__entity-result-list > li").all()
                        if not results: results = page.locator("div[data-view-name='people-search-result']").all()
                        if not results: results = page.locator("ul.reusable-search__entity-result-list > li, li.reusable-search__result-container, div[data-view-name='people-search-result']").all()

                        log_info(f"Scanning {len(results)} results...", module="MAIN")
                        
                        for res in results:
                            # Quick check
                            if msvcrt.kbhit():
                                if msvcrt.getch().decode('utf-8').lower() == 'q': raise KeyboardInterrupt("Quit")

                            try:
                                link_el = res.locator("a[href*='/in/']").first
                                if not link_el.is_visible(): continue
                                raw_url = link_el.get_attribute("href")
                                if not raw_url: continue
                                url = raw_url.split("?")[0].rstrip("/")
                                if "/in/" not in url: continue
                                if not url.startswith("http"): url = "https://www.linkedin.com" + url
                                
                                if sheets_client.is_profile_processed(url): continue

                                # Check Connect
                                has_connect = False
                                if res.locator("div[data-view-name='edge-creation-connect-action']").count() > 0: has_connect = True
                                elif res.get_by_role("button", name=re.compile(r"(^Connect|Invite .+ to connect)", re.IGNORECASE)).count() > 0: has_connect = True
                                elif res.get_by_role("link", name=re.compile(r"(^Connect|Invite .+ to connect)", re.IGNORECASE)).count() > 0: has_connect = True
                                elif res.locator("button[aria-label*='to connect'], a[aria-label*='to connect']").count() > 0: has_connect = True # Simplified
                                
                                if not has_connect:
                                    candidates_btn = res.locator("button, a").filter(has_text=re.compile(r"Connect", re.IGNORECASE)).all()
                                    for b in candidates_btn:
                                        if b.is_visible() and "Connect" in b.inner_text() and "Connected" not in b.inner_text():
                                            has_connect = True
                                            break
                                
                                if has_connect:
                                    candidates.append({"url": url, "element": link_el})

                            except: continue
                            
                        log_info(f"Found {len(candidates)} candidates.", module="MAIN")
                        if not candidates: human_scroll(page)
                    
                    except Exception as e:
                        log_warn(f"Error checking page {page_num}: {e}", module="MAIN")
                        break

                    # ACTION STEP
                    for i, candidate in enumerate(candidates):
                        # Use interruptible sleep for breaks? 
                        # Or check input before action
                        cmd = check_keyboard_input()
                        if cmd == 's': 
                            log_info("Skipping remaining candidates...", module="INPUT")
                            break
                        if cmd == 'q': raise KeyboardInterrupt("Quit command received")

                        url = candidate["url"]
                        link_el = candidate["element"]
                        
                        count_visits = state_manager.get_var("daily_visits_count", 0)
                        if count_visits >= CONFIG["LIMITS"]["PROFILE_VISITS_PER_DAY"]:
                            log_warn("Daily visit limit reached.", module="MAIN")
                            break

                        if rate_limiter.can_perform("profile_visits"):
                            log_info(f"[{i+1}/{len(candidates)}] Processing: {url}", module="MAIN")
                            
                            new_page = None
                            try:
                                try: link_el.scroll_into_view_if_needed()
                                except: pass
                                
                                with page.context.expect_page() as new_page_info:
                                    # Small sleep before click
                                    if interruptible_sleep(random.uniform(0.5, 1.5)) == 'q': raise KeyboardInterrupt
                                    link_el.click(modifiers=["Control"])
                                
                                new_page = new_page_info.value
                                new_page.wait_for_load_state()
                                
                                visited = visit_profile(new_page, url, captcha_detector, skip_navigation=True)
                                
                                if visited:
                                    rate_limiter.increment("profile_visits")
                                    if sheets_client:
                                         import datetime
                                         row = [str(datetime.datetime.now()), "VISIT", url, "SUCCESS", "N/A"]
                                         sheets_client.append_interaction(row)
                                    
                                    data = extract_profile_data(new_page)
                                    if rate_limiter.can_perform("connections"):
                                        note = generate_note(data)
                                        sent = send_connection_request(new_page, note, rate_limiter)
                                        status = "SENT" if sent else "SKIPPED/FAILED"
                                        sheets_client.append_profile_request(data, note, status)
                                
                                new_page.close()
                                page.bring_to_front()
                                
                            except Exception as px_e:
                                log_error(f"Error in tab: {px_e}", module="MAIN")
                                if new_page:
                                    try: new_page.close()
                                    except: pass
                                page.bring_to_front()

                        # Interruptible long sleep between profiles
                        wait_time = random.randint(10, 25)
                        log_info(f"Waiting {wait_time}s...", module="MAIN")
                        res = interruptible_sleep(wait_time)
                        if res == 'q': raise KeyboardInterrupt("Quit")
                        if res == 's': 
                             log_info("Skipping wait/next...", module="INPUT")
                             # 's' during wait might just skip the wait, or skip to next candidate? 
                             # Let's say it skips the wait.
                             pass

                    log_info("Finished page. Next...", module="MAIN")

                state_manager.set_var("search_term_index", idx + 1)
            
            # 6. Random Long Break
            log_info("Taking long break...", module="MAIN")
            # We need to manually handle this if we want it interruptible, 
            # OR we trust the "q" check before it? 
            # scheduler.take_random_break uses regular sleep. 
            # Let's override or just sleep here.
            # scheduler.take_random_break("LONG_BREAK") 
            # -> let's do manual interruptible sleep
            # config defaults might be 10-20 mins? 
            # Let's allow skip 's' to skip break.
            
            break_duration = random.randint(CONFIG["DELAYS"]["LONG_BREAK_MIN"], CONFIG["DELAYS"]["LONG_BREAK_MAX"])
            log_info(f"Long Break: {break_duration}s (Press 's' to skip)", module="SCHEDULER")
            if interruptible_sleep(break_duration) == 'q': break
            
    except KeyboardInterrupt:
        log_info("Manual Stop detected (or 'q' pressed).")
    except Exception as e:
        log_fatal(f"CRITICAL SYSTEM FAILURE: {e}")
        notifier.send_alert("System Crash", str(e))
    finally:
        browser_manager.close_browser()
        log_info("System Shutdown.")

if __name__ == "__main__":
    main()
