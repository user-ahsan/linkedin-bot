import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

CONFIG = {
    "ENABLE_AUTOMATION": True,
    "ENABLE_EMAIL_ALERTS": True,
    "EMAIL_ON_CAPTCHA": True,
    
    "BROWSER": {
        "HEADLESS": False, # Explicitly set to False for headful mode as requested
        "USER_DATA_DIR": "./browser_profile",
    },
    
    "SCHEDULER": {
        "START_HOUR": None,   # Set to None for 24/7 mode
        "END_HOUR": 18,
        "TIMEZONE": "Asia/Karachi"
    },
    
    "LIMITS": {
        "LIKES_PER_DAY": 10000,
        "PROFILE_VISITS_PER_DAY": 10000,
        "CONNECTIONS_PER_DAY": 10000
    },
    
    "DELAYS": {
        "ACTION_MIN": 2.5,
        "ACTION_MAX": 6.5,
        "SHORT_BREAK_MIN": 5,    # Seconds
        "SHORT_BREAK_MAX": 10,
        "LONG_BREAK_MIN": 10,    # Seconds
        "LONG_BREAK_MAX": 15
    },
    
    "EMAIL": {
        "TO": os.getenv("EMAIL_TO", "your@email.com"),
        "SMTP_SERVER": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "PORT": int(os.getenv("SMTP_PORT", 587)),
        "FROM": os.getenv("EMAIL_FROM", "notifier@bot.com"),
        "PASSWORD": os.getenv("EMAIL_PASSWORD", "")
    },

    "LLM": {
        "API_KEY": os.getenv("OPENAI_API_KEY", ""), # Leave empty to disable smart notes
        "MODEL": "gpt-3.5-turbo",
        "ENABLE_SMART_NOTES": True # Set to False to force skip note generation
    },
    
    "LINKEDIN": {
        "EMAIL": os.getenv("LINKEDIN_EMAIL", ""),
        "PASSWORD": os.getenv("LINKEDIN_PASSWORD", ""),
        "RETRY_LOGIN": True
    },

    "GSPREAD": {
        "CREDENTIALS_FILE": "credentials.json",
        "SHEET_NAME": "LinkedinBotData"
    },
    
    "SEARCH_SETTINGS": {
        "SCROLL_LOOPS": 2,           # Scrolls per search page
        "MAX_PROFILES_PER_SEARCH": 5,# Visit limit per keyword cycle
        "MAX_CONNECTIONS_PER_SEARCH": 3,
        "LOCATION": "Saudia Arabia",      # Default location filter
    },

    "RUN_MODE": "ALL", # Options: "ALL", "FEED_ONLY", "SEARCH_ONLY"

    "EXTRACTION": {
        "MAX_SCROLLS": 2,            # Limit scroll depth on profile
        "SAFE_MODE": True,           # If True, minimizes clicks (no "show more" expansion)
        "MIN_WAIT": 3,               # Min reading time per section
    }
}

def validate_config():
    """Validates the configuration for critical errors."""
    errors = []
    
    # Validate Scheduler
    if CONFIG["SCHEDULER"]["START_HOUR"] >= CONFIG["SCHEDULER"]["END_HOUR"]:
        errors.append("Scheduler: START_HOUR must be less than END_HOUR")
        
    # Validate Limits
    if CONFIG["LIMITS"]["LIKES_PER_DAY"] < 0:
         errors.append("Limits: LIKES_PER_DAY cannot be negative")

    # Fallback: Disable email if password is missing
    if not CONFIG["EMAIL"]["PASSWORD"]:
        # Don't error, just disable features
        CONFIG["ENABLE_EMAIL_ALERTS"] = False
        print("NOTE: Email password not found. Email alerts disabled.")

    # Fallback: Disable Smart Notes if API Key is missing
    if not CONFIG["LLM"]["API_KEY"]:
        CONFIG["LLM"]["ENABLE_SMART_NOTES"] = False
        print("NOTE: OpenAI API Key not found. Smart notes disabled.")


    return len(errors) == 0, errors

if __name__ == "__main__":
    is_valid, errs = validate_config()
    if is_valid:
        print("Config is valid.")
    else:
        print("Config validation failed:")
        for err in errs:
            print(f"- {err}")
