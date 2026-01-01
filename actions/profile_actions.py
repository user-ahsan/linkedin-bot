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
            # Try multiple selectors for top card
            page.wait_for_selector('section.pv-top-card, .pv-top-card--list, main section.artdeco-card', timeout=CONFIG["EXTRACTION"]["WAIT_TIMEOUT"])
        except:
            log_warn("Top card not found.", module="PROFILE")
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
        
        # DEBUG: If name is empty, dump HTML to see why
        if not data["full_name"]:
             log_warn("Extracted name is empty! Dumping HTML for debugging...", module="PROFILE")

        
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

# --- Sub-Extraction Functions ---

def _extract_identity(page, data):
    try:
        # Full Name (h1 is the standard accessible name for the profile)
        h1 = page.get_by_role("heading", level=1).first
        if h1.count() > 0:
            data["full_name"] = h1.inner_text().strip()
            data["first_name"] = data["full_name"].split(" ")[0]
            
        # Top Card Context
        # We need the context to find generic elements like headline/location
        # Using a broad selector but prioritizing the one containing the H1 we found
        if h1.count() > 0:
            top_card = page.locator("section, div").filter(has=h1).first
        else:
            top_card = page.locator("section.pv-top-card").first

        if top_card.is_visible():
            # Headline
            headline_elem = top_card.locator(".text-body-medium, [data-generated-suggestion-target]").first
            if headline_elem.is_visible():
                 data["headline"] = headline_elem.inner_text().strip()
                 
            # Location
            loc_elem = top_card.locator(".text-body-small").filter(has_text=re.compile(r",")).first
            if loc_elem.is_visible():
                 data["location"] = loc_elem.inner_text().strip()
                 
            # Connection Degree (Badge)
            dist_span = top_card.locator(".dist-value").first
            if dist_span.is_visible():
                data["connection_degree"] = dist_span.inner_text().strip()
            
    except Exception as e:
        log_warn(f"Identity extraction partial fail: {e}", module="PROFILE")

def _extract_about(page, data):
    try:
        # Use Accessible Heading
        about_header = page.get_by_role("heading", name=re.compile(r"^About$", re.IGNORECASE)).first
        
        if about_header.is_visible():
             # Find parent section
             section = page.locator("section").filter(has=about_header).first
             
             if section.is_visible():
                  # Expand
                  see_more = section.get_by_role("button", name=re.compile("see more", re.IGNORECASE))
                  if see_more.count() > 0 and not CONFIG["EXTRACTION"]["SAFE_MODE"]:
                      try: see_more.first.click(timeout=1000)
                      except: pass

                  # Text
                  # Often in a span with 'visually-hidden' is the full text? No, usually main text.
                  description_box = section.locator(".inline-show-more-text, .pv-about__summary-text").first
                  if description_box.is_visible():
                       raw_text = description_box.inner_text()
                  else:
                       raw_text = section.inner_text()
                  
                  clean_text = raw_text.replace("About", "").replace("see more", "").replace("...", "").strip()
                  data["about_text"] = clean_text[:800]
                  
    except Exception as e:
        log_warn(f"About extraction failed: {e}", module="PROFILE")

def _extract_experience(page, data):
    try:
        page.mouse.wheel(0, 500)
        time.sleep(1)
        
        # Accessible Heading
        xp_header = page.get_by_role("heading", name=re.compile(r"^Experience$", re.IGNORECASE)).first
        
        if xp_header.is_visible():
             # Find section
             xp_section = page.locator("section").filter(has=xp_header).first
             if xp_section.is_visible():
                 # Items
                 items = xp_section.locator("ul.pvs-list > li").all()
                 if items:
                      first_item = items[0]
                      # Use span text with aria-hidden="true" usually contains visual noise, but let's grab all text
                      # Better yet: get the screen reader text? 
                      # The structure is usually:
                      # div > span.visually-hidden (The full structured string)
                      
                      sr_span = first_item.locator("span.visually-hidden").first
                      if sr_span.is_visible():
                          # "Position: Title, Company: Name..."
                          full_text = sr_span.inner_text()
                          # Parse logic for SR text if possible, else fallback to visual
                          data["latest_job_title"] = full_text[:50] # Placeholder logic
                          
                      # Visual Fallback (standard)
                      text_lines = first_item.inner_text().split("\n")
                      clean_lines = [l.strip() for l in text_lines if l.strip() and "Experience" not in l]
                      
                      if len(clean_lines) > 0: data["latest_job_title"] = clean_lines[0]
                      if len(clean_lines) > 1: data["latest_company"] = clean_lines[1].split("·")[0].strip()
                      if len(clean_lines) > 2: data["latest_job_duration"] = clean_lines[2]

        else:
            # Anchor check
            if page.locator("#experience").count() > 0:
                 pass # Use ID anchor logic if needed
            else:
                 log_warn("Experience section not found (Accessible).", module="PROFILE")

    except Exception as e:
        log_warn(f"Experience extraction failed: {e}", module="PROFILE")

def _extract_skills(page, data):
    try:
        # Find Skills section
        skills_header = page.get_by_role("heading", name=re.compile(r"^Skills$", re.IGNORECASE)).first
        
        if skills_header.is_visible():
             skills_section = page.locator("section").filter(has=skills_header).first
             
             # Items
             # Accessible items often have aria-label
             skill_items = skills_section.locator("ul.pvs-list > li").all()
             found = []
             
             for item in skill_items[:5]:
                 # Try finding the accessible name first
                 # e.g. link with aria-label="Skill: Python"
                 link = item.locator("a[aria-label]").first
                 if link.is_visible():
                     label = link.get_attribute("aria-label")
                     if label: found.append(label.split("Skill: ")[-1]) # Heuristic
                     continue
                     
                 # Fallback to visual text
                 txt = item.inner_text().strip().split("\n")[0]
                 if txt: found.append(txt)
                 
             data["top_skills"] = ", ".join(list(set(found)))
             
    except Exception as e:
        log_warn(f"Skills extraction failed: {e}", module="PROFILE")

def _extract_activity(page, data):
    try:
         # 1. From Top Card (Connections)
         top_card = page.locator("section.pv-top-card").first
         if top_card.is_visible():
             text = top_card.inner_text()
             conn = re.search(r"(\d{1,3}(?:,\d{3})*\+?)\s+connections", text)
             if conn: data["connections_count"] = conn.group(1)

         # 2. From Activity Section
         act_header = page.get_by_role("heading", name=re.compile(r"^Activity$", re.IGNORECASE)).first
         if act_header.is_visible():
             act_section = page.locator("section").filter(has=act_header).first
             text = act_section.inner_text()
             foll = re.search(r"([\d,]+)\s+followers", text)
             if foll: data["followers_count"] = foll.group(1)
             
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
