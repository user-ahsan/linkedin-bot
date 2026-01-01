import time
from core.logger import log_info, log_error
from core.human_actions import random_delay, human_scroll
from core.captcha_detector import CaptchaDetector

def visit_profile(page, url, captcha_detector: CaptchaDetector):
    try:
        log_info(f"Visiting profile: {url}", module="PROFILE")
        page.goto(url)
        captcha_detector.check_for_captcha(page)
        random_delay("ACTION")
        human_scroll(page)
        return True
    except Exception as e:
        log_error(f"Failed to visit profile: {e}", module="PROFILE")
        return False

def extract_profile_data(page):
    """
    Extracts visible data: Name, Headline, About, Skills.
    """
    data = {
        "name": "",
        "headline": "",
        "about": "",
        "skills": [],
        "url": page.url
    }
    
    try:
        # Common selectors (fragile, subject to change)
        
        # Name: usually h1
        name_elem = page.locator("h1.text-heading-xlarge") # Example selector
        if name_elem.count() > 0:
            data["name"] = name_elem.first.inner_text().strip()
        else:
             # Fallback
             data["name"] = page.title().split("|")[0].strip()

        # Headline
        headline_elem = page.locator("div.text-body-medium") # Detailed selectors needed
        if headline_elem.count() > 0:
            data["headline"] = headline_elem.first.inner_text().strip()
            
        # About
        # Look for the "About" section div
        # Usually it's a section with an id 'about' or checking for h2 with text "About"
        try:
             about_section = page.locator('section').filter(has=page.locator('h2', has_text="About"))
             if about_section.count() > 0:
                  # Text body is usually in a div or span
                  # Might need to click "see more" if truncated?
                  # For now, get visible text.
                  data["about"] = about_section.first.inner_text().replace("About\n", "").strip()
        except: pass

        # Skills
        # Look for "Skills" section
        try:
             # Often in a section with h2 "Skills"
             skills_section = page.locator('section').filter(has=page.locator('h2', has_text="Skills"))
             if skills_section.count() > 0:
                  # Get list items
                  # Usually ul > li > ... span[aria-hidden="true"]
                  # Retrieve first 5 visible skills
                  skill_texts = skills_section.first.locator('span[aria-hidden="true"]').all_inner_texts()
                  # Filter out structural text or "Endorsed by"
                  # Heuristic: simple non-empty strings
                  clean_skills = [s.strip() for s in skill_texts if len(s) > 2 and "Endorsed" not in s][:5]
                  data["skills"] = list(set(clean_skills)) # Dedup
        except: pass
        
        log_info(f"Extracted data for {data['name']}", module="PROFILE")
        return data
        
    except Exception as e:
        log_error(f"Extraction error: {e}", module="PROFILE")
        return data
