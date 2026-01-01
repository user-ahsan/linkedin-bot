from config.config import CONFIG
from core.logger import log_info, log_error, log_warn

# try:
#     import openai
# except ImportError:
#     openai = None

def generate_note(profile_data):
    """
    Generates a connection note using LLM.
    Returns empty string if disabled or failed, triggering 'Send without note' fallback.
    """
    if not CONFIG["LLM"].get("ENABLE_SMART_NOTES", True):
        log_info("Smart notes disabled in config. Skipping generation.", module="LLM")
        return ""
        
    api_key = CONFIG["LLM"]["API_KEY"]
    if not api_key:
        log_warn("No LLM API Key found (and somehow enabled). returning empty note.", module="LLM")
        return ""
        
    # Mock return for now to ensure safety without real API calls in dev
    # In prod, uncomment openai call
    
    name = profile_data.get("name", "there")
    
    note = f"Hi {name}, I noticed your profile and was impressed by your work. I'd love to connect and keep in touch."
    log_info(f"Generated note: {note}", module="LLM")
    return note
