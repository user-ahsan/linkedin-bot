import time
import sys
import os
import random
import re

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
from storage.sheets_client import SheetsClient

from actions.feed_actions import run_feed_cycle
from actions.search_people import perform_search
from actions.profile_actions import visit_profile, extract_profile_data
from actions.note_generator import generate_note
from actions.connect_actions import send_connection_request
from actions.auth_actions import login_to_linkedin, check_session_health

def main():
    log_info("BOOT: LinkedIn Autonomous Agent Starting...")
    
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
            # Check validity
            if not check_session_health(page):
                log_warn("Session invalid. Re-attempting login...")
                if not login_to_linkedin(page):
                    log_fatal("Re-login failed.")
                    break
            # 1. Check Active Hours
            if not scheduler.is_within_active_hours():
                log_info("Active hours ended. Sleeping/Exiting...")
                time.sleep(600)
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
                # State has search_term_index
                idx = state_manager.get_var("search_term_index", 0)
                if idx >= len(keywords):
                    idx = 0
                
                keyword = keywords[idx]
                log_info(f"Starting Search Cycle for: {keyword}")
                
                if sheets_client:
                     import datetime
                     row = [str(datetime.datetime.now()), "SEARCH", keyword, "STARTED", "N/A"]
                     sheets_client.append_interaction(row)
                
                # PAGINATION LOOP (Exhaustive)
                # Max 100 pages or until no results
                for page_num in range(1, 101):
                    log_info(f"Processing Page {page_num} for keyword: {keyword}", module="MAIN")
                    
                    if page_num == 1:
                        scroll_loops = CONFIG["SEARCH_SETTINGS"].get("SCROLL_LOOPS", 2)
                        success = perform_search(page, keyword, captcha_detector, scroll_loops)
                        if not success:
                            break # Skip to next keyword if initial search fails
                    else:
                        # Navigate to next page using URL param
                        # We need the current base URL. 
                        # Assuming we are on a search results page
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
                        time.sleep(random.randint(5, 8))
                        captcha_detector.check_for_captcha(page)
                        human_scroll(page)
                    
                    # Process Results on Current Page
                    # -------------------------------
                    # Collect profiles
                    try:
                        # Wait for results to be visible (Any common marker)
                        page.wait_for_selector("li.reusable-search__result-container, [data-test-app-aware-link]", timeout=30000)
                    except Exception as e:
                        log_warn(f"No results found on page {page_num} (Timeout: {e}). Ending pagination for {keyword}.", module="MAIN")
                        break

                    # Precise Selector: Only get the TITLE link of the result.
                    # This avoids "Mutual connection" links or extraction of non-target profiles.
                    links = page.locator("span.entity-result__title-text a.app-aware-link").all()
                    
                    # Robust Fallback (if title text structure changes, fall back to container logic)
                    if not links:
                         log_warn("Standard title links not found, falling back to broad search.", module="MAIN")
                         links = page.locator("li.reusable-search__result-container a.app-aware-link").all()

                    # Deduplicate links in current view
                    # Filter for specific profile links
                    valid_links = []
                    for link in links:
                        try:
                             href = link.get_attribute("href")
                             if href:
                                 # Normalize FIRST before check
                                 clean_url = href.split("?")[0].rstrip("/")
                                 if "/in/" in clean_url and "linkedin.com" in clean_url:
                                     valid_links.append(link)
                        except: continue
                    
                    # Unique by Href
                    unique_links = {}
                    for link in valid_links:
                        h = link.get_attribute("href").split('?')[0]
                        if h not in unique_links:
                            unique_links[h] = link
                    
                    final_links = list(unique_links.values())
                    count_found = len(final_links)
                    log_info(f"Found {count_found} profiles on page {page_num}.", module="MAIN")
                    
                    if count_found == 0:
                        log_info("Zero valid profiles found. Ending pagination.", module="MAIN")
                        break

                    # Loop through profiles on this page
                    for link in final_links:
                        # 1. URL Normalization & Dupe Check
                        raw_url = link.get_attribute("href")
                        url = raw_url.split("?")[0].rstrip("/")
                        
                        if sheets_client.is_profile_processed(url):
                             log_info(f"Skipping (Dup): {url}", module="MAIN")
                             continue
                        
                        # 2. STRICT CONNECT CHECK (No Visit if not Connect)
                        # Find container
                        try:
                             # Flexible Ancestor Search
                             container = link.locator("xpath=./ancestor::li[contains(@class, 'reusable-search__result-container')] | ./ancestor::div[contains(@class, 'entity-result')]")
                             if container.count() > 0:
                                 container = container.first # Take the closest one if ambiguous
                                 
                                 # Get all visible buttons in actions area
                                 # .entity-result__actions is standard, but fallback to just 'button' in container
                                 actions_area = container.locator(".entity-result__actions")
                                 if actions_area.count() == 0:
                                      actions_area = container # Fallback to search whole container
                                 
                                 # If we have a "Connect" button, we proceed.
                                 # If we see "Message", "Follow", "Pending", we skip.
                                 
                                 # Get all text from buttons to debug
                                 all_buttons_text = actions_area.locator("button").all_inner_texts()
                                 
                                 # Check if "Connect" is in any of the button texts
                                 # STRICT CHECK: Ensure it is "Connect" and not "Connected"
                                 # we look for pure "Connect" or "Connect" with whitespace
                                 has_connect = False
                                 for btn_text in all_buttons_text:
                                     clean_text = btn_text.strip().lower()
                                     # Exact match for "connect" to avoid "connected" or "pending" (if logic changes)
                                     if clean_text == "connect":
                                         has_connect = True
                                         break

                                 if not has_connect:
                                      log_info(f"Skipping (No Connect Button). Found: {all_buttons_text}. URL: {url}", module="MAIN")
                                      continue
                                 
                        except Exception as e:
                             log_warn(f"Button check failed: {e}. Skipping safely.", module="MAIN")
                             continue
                             
                        # 3. Visit & Connect
                        if rate_limiter.can_perform("profile_visits"):
                            visited = visit_profile(page, url, captcha_detector)
                            if visited:
                                rate_limiter.increment("profile_visits")
                                
                                if sheets_client:
                                     import datetime
                                     row = [str(datetime.datetime.now()), "VISIT", url, "SUCCESS", "N/A"]
                                     sheets_client.append_interaction(row)
                                
                                # Extract
                                data = extract_profile_data(page)
                                
                                # Connect
                                if rate_limiter.can_perform("connections"):
                                    note = generate_note(data)
                                    sent = send_connection_request(page, note, rate_limiter)
                                    
                                    status = "SENT" if sent else "SKIPPED/FAILED"
                                    sheets_client.append_profile_request(data, note, status)
                                
                        time.sleep(random.randint(3, 7))

                # Update index ONLY after finishing all pages for this keyword
                state_manager.set_var("search_term_index", idx + 1)
            
            # 6. Random Long Break
            scheduler.take_random_break("LONG_BREAK")
            
    except KeyboardInterrupt:
        log_info("Manual Stop detected.")
    except Exception as e:
        log_fatal(f"CRITICAL SYSTEM FAILURE: {e}")
        notifier.send_alert("System Crash", str(e))
    finally:
        browser_manager.close_browser()
        log_info("System Shutdown.")

if __name__ == "__main__":
    main()
