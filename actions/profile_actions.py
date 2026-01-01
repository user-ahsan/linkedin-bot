import time
import re
from core.logger import log_info, log_error, log_warn
from core.human_actions import random_delay, human_scroll
from core.captcha_detector import CaptchaDetector
from config.config import CONFIG

def visit_profile(page, url, captcha_detector: CaptchaDetector):
    """
    Navigates to a profile with safety checks.
    """
    try:
        log_info(f"Visiting profile: {url}", module="PROFILE")
        # 2.1 Navigation (domcontentloaded is faster/safer than networkidle)
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=CONFIG["EXTRACTION"]["WAIT_TIMEOUT"] + 5000)
        except Exception as e:
             log_warn(f"Page load timeout/error: {e}", module="PROFILE")

        # 2.2 Page Validation (Abort Early)
        # Check for unavailable or captcha
        if "unavailable" in page.title().lower() or page.locator("h1").filter(has_text="Profile not available").count() > 0:
             log_warn("Profile unavailable.", module="PROFILE")
             return False

        captcha_detector.check_for_captcha(page)
        
        # Check if we are actually on a profile (presence of top card)
        try:
            page.wait_for_selector('section.pv-top-card', timeout=CONFIG["EXTRACTION"]["WAIT_TIMEOUT"])
        except:
            log_warn("Top card not found. Might not be a profile page.", module="PROFILE")
            return False

        random_delay("ACTION")
        return True
    except Exception as e:
        log_error(f"Failed to visit profile: {e}", module="PROFILE")
        return False

def extract_profile_data(page):
    """
    Step-by-step extraction of profile data following the Safe Mode protocol.
    """
    data = {
        "profile_url": page.url,
        "linkedin_id": "", # To be derived
        "full_name": "", "first_name": "", "connection_degree": "", "location": "",
        "headline": "", "current_role": "", "current_company": "", "industry_keywords": "", "persona_type": "",
        "about_text": "", "about_keywords": "", "years_of_experience": "", "seniority_level": "",
        "latest_job_title": "", "latest_company": "", "latest_job_duration": "", "previous_company": "",
        "top_skills": "", "skill_types": "",
        "recent_post_snippet": "", "recent_post_topic": "", "followers_count": "", "connections_count": "",
        "extracted_at": "", "profile_status": "extracted", 
        "message_sent": False, "reply_received": False, "last_action": "", "notes": ""
    }
    
    try:
        # Derive LinkedIn ID from URL
        if "/in/" in page.url:
            data["linkedin_id"] = page.url.split("/in/")[1].split("/")[0]

        # 3.1 TOP CARD (MANDATORY)
        _extract_identity(page, data)
        
        # 3.2 ABOUT SECTION
        _extract_about(page, data)
        
        # 3.3 EXPERIENCE (LATEST ONLY)
        _extract_experience(page, data)
        
        # 3.4 & 3.5 SKILLS (SAFE MODE)
        _extract_skills(page, data)
        
        # 3.6 ACTIVITY
        _extract_activity(page, data)
        
        # 4. DERIVED FIELDS
        _compute_derived_fields(data)
        
        log_info(f"Extracted complete profile for {data['full_name']}", module="PROFILE")
        return data
        
    except Exception as e:
        log_error(f"Critical Extraction Error: {e}", module="PROFILE")
        data["profile_status"] = "error"
        return data

# --- Sub-Extraction Functions ---

def _extract_identity(page, data):
    try:
        top_card = page.locator("section.pv-top-card").first
        if not top_card.is_visible(): return
        
        # Full Name (h1)
        h1 = top_card.locator("h1")
        if h1.count() > 0:
            data["full_name"] = h1.inner_text().strip()
            data["first_name"] = data["full_name"].split(" ")[0]
            
        # Headline & Location
        # Finding the left panel text details
        # Often it's in a div with class 'pv-text-details__left-panel'
        left_panel = top_card.locator("div.pv-text-details__left-panel").first
        if left_panel.is_visible():
             headline_elem = left_panel.locator("div.text-body-medium")
             if headline_elem.count() > 0:
                 data["headline"] = headline_elem.first.inner_text().strip()
                 
             loc_elem = left_panel.locator("span.text-body-small")
             if loc_elem.count() > 0:
                 # It might be the second span? Usually the one that is NOT the connection distance
                 # Let's take the text that looks like a location (contains comma or Pakistan)
                 data["location"] = loc_elem.first.inner_text().strip()
                 
        # Connection Degree (Badge)
        # Usually a span with class 'dist-value' or inside the name badge
        dist_span = top_card.locator("span.dist-value") 
        if dist_span.count() > 0:
            data["connection_degree"] = dist_span.first.inner_text().strip()
            
    except Exception as e:
        log_warn(f"Identity extraction partial fail: {e}", module="PROFILE")

def _extract_about(page, data):
    try:
        # Find About section
        # Strategy: Look for h2 "About" and get sibling/parent context
        about_header = page.locator("div#about, section#about, h2").filter(has_text=re.compile(r"^About$", re.IGNORECASE)).first
        if not about_header.is_visible():
             # Try searching by ID
             about_header = page.locator("div#about").first
             
        if about_header.is_visible():
             # The text is usually in a sibling div or inside the section
             # We look for the nearest 'span' or 'div' with meaningful text
             # Playwright: locate the section container first
             section = page.locator("section").filter(has=page.locator("div#about")).first
             if not section.is_visible():
                  # Fallback: locate section that *contains* the h2 "About"
                  section = page.locator("section").filter(has=page.locator("h2", has_text="About")).first
             
             if section.is_visible():
                  # Expand if needed (Safe Mode check)
                  see_more = section.locator("button.inline-show-more-text__button")
                  if see_more.count() > 0 and not CONFIG["EXTRACTION"]["SAFE_MODE"]:
                      see_more.first.click()
                      time.sleep(0.5)
                      
                  # Extract text (often in a span with aria-hidden=true? No, visual text)
                  # Simplest: section.inner_text() minus "About"
                  raw_text = section.inner_text()
                  clean_text = raw_text.replace("About", "").replace("see more", "").strip()
                  data["about_text"] = clean_text[:500] # Limit char count
                  
    except Exception as e:
        log_warn(f"About extraction failed: {e}", module="PROFILE")

def _extract_experience(page, data):
    try:
        # 1. Scroll Once
        page.mouse.wheel(0, 600)
        time.sleep(2) # Config wait?
        
        # 2. Find Experience Section
        xp_section = page.locator("section#experience").first
        if not xp_section.is_visible():
             # Fallback
             xp_section = page.locator("section").filter(has=page.locator("h2", has_text="Experience")).first
             
        if xp_section.is_visible():
             # 3. Extract FIRST role only
             # Usually a list: ul > li
             first_li = xp_section.locator("ul.pvs-list > li").first
             if first_li.is_visible():
                  # Inside the Li, there are usually spans for Title, Company, Date
                  # Scrape all text lines and infer
                  lines = first_li.inner_text().split("\n")
                  # Heuristic: 
                  # Line 0: Job Title (usually)
                  # Line 1: Company Name • Employment Type
                  # Line 2: Date
                  
                  # BUT: Structure varies if threaded (multiple roles same company)
                  # If threaded, First line is Company, Second is Role?
                  
                  # Simplification for robustness:
                  # Just Grab the first 3 non-empty lines and store them.
                  clean_lines = [l.strip() for l in lines if l.strip() and "Experience" not in l and "Show all" not in l]
                  
                  if len(clean_lines) >= 1: data["latest_job_title"] = clean_lines[0]
                  if len(clean_lines) >= 2: data["latest_company"] = clean_lines[1]
                  if len(clean_lines) >= 3: data["latest_job_duration"] = clean_lines[2]
                  
    except Exception as e:
        log_warn(f"Experience extraction failed: {e}", module="PROFILE")

def _extract_skills(page, data):
    try:
        # Find Skills section
        skills_section = page.locator("section").filter(has=page.locator("h2", has_text="Skills")).first
        if skills_section.is_visible():
             # Get visible skills (li items or spans)
             # Typical structure: ul > li > ... > span[aria-hidden="true"]
             skill_elements = skills_section.locator("span[aria-hidden='true']").all()
             
             found_skills = []
             for el in skill_elements:
                 if len(found_skills) >= 5: break
                 txt = el.inner_text().strip()
                 if len(txt) > 2 and "Endorsement" not in txt and "Skill" not in txt:
                     found_skills.append(txt)
                     
             data["top_skills"] = ", ".join(list(set(found_skills)))
             
    except Exception as e:
        log_warn(f"Skills extraction failed: {e}", module="PROFILE")

def _extract_activity(page, data):
    try:
         # Try to find follower count in top card (often "500+ connections")
         top_card = page.locator("section.pv-top-card").first
         if top_card.is_visible():
              # Look for text containing "connections" or "followers"
              text_content = top_card.inner_text()
              
              # Connections
              conn_match = re.search(r"(\d+\+?)\s+connections", text_content)
              if conn_match:
                  data["connections_count"] = conn_match.group(1)
                  
              # Followers
              foll_match = re.search(r"([\d,]+)\s+followers", text_content)
              if foll_match:
                  data["followers_count"] = foll_match.group(1)
                  
    except Exception as e:
        log_warn(f"Activity extraction failed: {e}", module="PROFILE")

def _compute_derived_fields(data):
    """
    Computes/Infers fields based on extracted raw data.
    """
    # 1. Persona
    title = data["latest_job_title"].lower() + " " + data["headline"].lower()
    
    if "founder" in title or "co-founder" in title or "owner" in title:
        data["persona_type"] = "Founder"
    elif any(x in title for x in ["head of", "director", "vp", "chief", "manager"]):
        data["persona_type"] = "Decision Maker"
    elif "student" in title or "intern" in title:
        data["persona_type"] = "Student"
    else:
        data["persona_type"] = "Contributor"

    # 2. Seniority
    if any(x in title for x in ["senior", "principal", "staff"]):
        data["seniority_level"] = "Senior"
    elif any(x in title for x in ["junior", "associate", "graduate"]):
        data["seniority_level"] = "Junior"
    elif any(x in title for x in ["head", "lead", "director", "vp", "c-level"]):
        data["seniority_level"] = "Leadership"
    else:
        data["seniority_level"] = "Mid-Level"

    # 3. Industry (Simple heuristic from current company/headline)
    data["industry_keywords"] = "Tech" # Default for now, could be improved with lists
