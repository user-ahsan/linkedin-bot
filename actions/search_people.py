import time
import re
from core.logger import log_info, log_error, log_warn
from core.human_actions import random_delay, human_scroll, safe_click, type_text
from core.captcha_detector import CaptchaDetector

def perform_search(page, keyword, captcha_detector: CaptchaDetector):
    """
    Executes search for a keyword and filters by People and Location (Pakistan).
    Strictly follows Corrective Guidance Document.
    """
    try:
        log_info(f"Searching for: {keyword}", module="SEARCH")
        captcha_detector.check_for_captcha(page)
        
        # STEP 1: Search Query
        # Go to global search bar or URL
        log_info(f"step 1: navigating to search for {keyword}", module="SEARCH")
        page.goto(f"https://www.linkedin.com/search/results/all/?keywords={keyword}")
        time.sleep(5) # Wait for page load
        captcha_detector.check_for_captcha(page)
        
        # STEP 2: Switch to "People" Tab
        log_info("step 2: switching to people tab", module="SEARCH")
        people_filter_btn = page.get_by_role("button", name="People", exact=True)
        if not people_filter_btn.is_visible():
             # Fallback
             people_filter_btn = page.locator('button:has-text("People")')
             
        if people_filter_btn.is_visible():
            people_filter_btn.click()
            time.sleep(4) # Wait to stabilize
        else:
            # Force URL navigation if button fails
            log_warn("people tab button not found, forcing url", module="SEARCH")
            page.goto(f"https://www.linkedin.com/search/results/people/?keywords={keyword}")
            time.sleep(5)
            
        # STEP 3: Open Location Filter Dropdown
        log_info("step 3: opening location filter", module="SEARCH")
        loc_btn = page.get_by_role("button", name="Locations")
        if not loc_btn.is_visible():
             # Try generic filter button if width is small?
             log_error("Location filter button not found", module="SEARCH")
             return False
             
        loc_btn.click()
        time.sleep(2) # Wait for dropdown UI

        # STEP 4: Type Location (Pakistan)
        # Try specific aria-label first, then placeholder
        loc_input = page.locator("input[aria-label='Add a location']")
        if not loc_input.is_visible():
            loc_input = page.get_by_placeholder("Add a location")
            
        if not loc_input.is_visible():
            log_error("[ERROR] Location input field not found", module="SEARCH")
            return False

        loc_input.fill("Pakistan")
        log_info("[FILTER] Typed location: Pakistan", module="SEARCH")
        time.sleep(3) # Wait for LinkedIn to fetch suggestions

        # STEP 5: SELECT FIRST LOCATION RESULT (CRITICAL)
        # Detect suggestion list implication by pressing ArrowDown
        loc_input.press("ArrowDown")
        time.sleep(1)
        loc_input.press("Enter")
        log_info("[FILTER] Location suggestion selected via ENTER", module="SEARCH")
        time.sleep(2)

        # STEP 6: Click "Show results" Button (MANDATORY)
        # Using regex to match "Show X results" or "Show X result"
        # Strategy: Find all candidates (text or aria-label), iterate, click first visible Primary button.
        
        # 1. Get candidates by role (covers aria-label which seems to be the case based on debugging)
        candidates_role = page.get_by_role("button", name=re.compile(r"Show .*result.*|Apply current filter", re.IGNORECASE)).all()
        
        # 2. Get candidates by text (fallback)
        candidates_text = page.locator("button").filter(has_text=re.compile(r"Show .*result.*", re.IGNORECASE)).all()
        
        all_candidates = candidates_role + candidates_text
        clicked = False
        
        for btn in all_candidates:
            try:
                # Check for Primary class to be safe?
                # class_attr = btn.get_attribute("class")
                # if "artdeco-button--primary" not in class_attr: continue
                
                if btn.is_visible():
                    # Double check it is the primary action if multiple visible?
                    # But usually only one "Show results" is visible in the filter dropdown.
                    btn.click()
                    log_info("[FILTER] Show results clicked", module="SEARCH")
                    clicked = True
                    break
            except Exception:
                continue
                
        if clicked:
            time.sleep(5) # Wait for reload / results refresh
        else:
            log_error("[ERROR] Show results button not found or not visible", module="SEARCH")
            
            # DEBUG: Dump HTML to analyze why selector failed
            try:
                with open("debug_search_page.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
                log_warn("Dumped page content to debug_search_page.html", module="SEARCH")
            except Exception as dump_err:
                log_error(f"Failed to dump HTML: {dump_err}", module="SEARCH")

            # Abort as per doc
            log_error("[ERROR] Location filter failed to apply – aborting flow", module="SEARCH")
            return False
            
        # STEP 7: Validate Filter Application
        current_url = page.url
        body_text = page.locator("body").inner_text()
        
        # Validation 1: URL should contain geoUrn (Pakistan is often 101022442, but dynamic) OR origin switch
        # Validation 2: "Pakistan" pill visible
        
        filter_pill = page.locator("button.artdeco-pill").filter(has_text="Pakistan")
        
        if "geoUrn" in current_url or filter_pill.count() > 0:
            log_info("[FILTER] Location filter applied successfully", module="SEARCH")
        else:
            # Check for result count refresh maybe?
            # If prompt says "strictly abort", we abort.
            # But let's be slightly robust: did the URL change at all?
            log_error("[ERROR] Location filter failed to apply (validation failed) – aborting flow", module="SEARCH")
            return False

        # STEP 8: Scroll Results
        log_info("scrolling results...", module="SEARCH")
        human_scroll(page)
        
        # STEP 9 Success
        return True

    except Exception as e:
        log_error(f"Search failed: {e}", module="SEARCH")
        return False
