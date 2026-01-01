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
from core.human_actions import human_scroll
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
                        # Wait for results to be visible
                        # We try a few common containers. 
                        # If specific classes fail, we wait for ANY link that looks like a profile
                        try:
                            page.wait_for_selector("ul.reusable-search__entity-result-list, .search-results-container, div.entity-result, a[href*='/in/']", timeout=15000)
                        except:
                            log_warn("Standard selectors timed out. Checking for page content...", module="MAIN")
                        
                        # Verify we actually have results by looking for profile links
                        # This is the ultimate fallback: if there are profile links, we have results.
                        profile_links_count = page.locator("a[href*='/in/']").count()
                        if profile_links_count == 0:
                             log_warn(f"No profile links found on page {page_num}.", module="MAIN")
                             break
                             
                    except Exception as e:
                        log_warn(f"Error checking results page {page_num}: {e}", module="MAIN")
                        break

                    # ---------------------------------------------------------
                    # SCAN STEP: Identify Candidates with "Connect" buttons
                    # ---------------------------------------------------------
                    candidates = []
                    
                    # Get all result containers (more stable than getting links first)
                    # We look for the main list items
                    # Try explicit list item selector first
                    results = page.locator("ul.reusable-search__entity-result-list > li").all()
                    
                    if not results:
                        results = page.locator("div[data-view-name='people-search-result']").all()

                    if not results:
                        # Fallback: custom list item role
                        # results = page.get_by_role("list").filter(has=page.locator("a[href*='/in/']")).first.get_by_role("listitem").all()
                        # Revert: The listitem role might be catching filtered out visible items or wrong lists
                        # Using the explicit class is safer for the *Container* identification
                        results = page.locator("ul.reusable-search__entity-result-list > li, li.reusable-search__result-container, div[data-view-name='people-search-result']").all()

                    log_info(f"Scanning {len(results)} results for 'Connect' buttons...", module="MAIN")
                    
                    for res in results:
                        try:
                            # 1. Extract URL (Robust)
                            link_el = res.locator("a[href*='/in/']").first
                            
                            if not link_el.is_visible(): continue
                            
                            raw_url = link_el.get_attribute("href")
                            if not raw_url: continue
                            
                            url = raw_url.split("?")[0].rstrip("/")
                            if "/in/" not in url or "linkedin.com" not in url:
                                if url.startswith("/in/"):
                                    url = "https://www.linkedin.com" + url
                                else:
                                    continue
                            
                            if sheets_client.is_profile_processed(url):
                                continue

                            # 2. Check for "Connect" Button (Accessible + Fallback)
                            has_connect = False
                            
                            # Strategy A: Role "button" (Standard accessibility)
                            if res.get_by_role("button", name=re.compile(r"^Connect", re.IGNORECASE)).count() > 0:
                                has_connect = True
                                
                            # Strategy B: Role "link" (LinkedIn often uses <a> for actions)
                            elif res.get_by_role("link", name=re.compile(r"^Connect", re.IGNORECASE)).count() > 0:
                                has_connect = True
                                
                            # Strategy C: Explicit Element Attributes (Aria-Label) on button OR link
                            if not has_connect:
                                if res.locator("button[aria-label^='Connect'], a[aria-label^='Connect']").count() > 0:
                                    has_connect = True

                            # Strategy D: Text Content (Fallback for stubborn elements)
                            if not has_connect:
                                # Look for "Connect" text but strictly avoid "Connected", "Disconnect"
                                # We check both button and a tags.
                                candidates_btn = res.locator("button, a").filter(has_text=re.compile(r"Connect", re.IGNORECASE)).all()
                                for b in candidates_btn:
                                    if b.is_visible():
                                        t = b.inner_text().strip()
                                        # Strict check: "Connect" must be distinct
                                        # e.g. "Connect", "Connect with John", but NOT "Connected"
                                        if "Connect" in t and "Connected" not in t and "Pending" not in t and "Message" not in t:
                                            has_connect = True
                                            break

                            if has_connect:
                                candidates.append(url)

                        except Exception as e:
                            log_warn(f"Error scanning result item: {e}", module="MAIN")
                            continue
                            
                    log_info(f"Found {len(candidates)} connectable profiles on this page.", module="MAIN")

                    if not candidates:
                        log_info("No candidates found, scrolling/moving to next page.", module="MAIN")
                        # Optional: Scroll one more time just in case? 
                        human_scroll(page)
                    
                    # ---------------------------------------------------------
                    # ACTION STEP: Process Candidates
                    # ---------------------------------------------------------
                    
                    # Store current Search URL to return to
                    search_page_url = page.url
                    
                    for i, url in enumerate(candidates):
                         # Double check limits
                        count_visits = state_manager.get_var("daily_visits_count", 0) # Just an example, or rely on rate_limiter
                        # Actually rate_limiter handles simple counts, but let's check config limits
                        
                        if count_visits >= CONFIG["LIMITS"]["PROFILE_VISITS_PER_DAY"]:
                            log_warn("Daily visit limit reached. Stopping search.", module="MAIN")
                            break

                        # Visit
                        if rate_limiter.can_perform("profile_visits"):
                            log_info(f"[{i+1}/{len(candidates)}] Processing: {url}", module="MAIN")
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
                                
                        # Random delay between profiles
                        time.sleep(random.randint(5, 10))

                    # End of Page Processing
                    # Restore Search Context for Next Page Navigation
                    log_info("Restoring search context...", module="MAIN")
                    try:
                        page.goto(search_page_url, wait_until='domcontentloaded')
                        time.sleep(3)
                    except Exception as nav_e:
                        log_warn(f"Failed to restore search context: {nav_e}", module="MAIN")
                    
                    # We continue loop to next page_num


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
