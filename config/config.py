import os
import json
import shutil
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.default.json') # Optional backup

def load_config():
    """Lengths configuration from config.json"""
    if not os.path.exists(CONFIG_FILE):
        # Create default if not exists
        return {}
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config.json: {e}")
        return {}

def save_config(new_config):
    """Saves configuration to config.json"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(new_config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config.json: {e}")
        return False

# Load Initial Config
CONFIG = load_config()

# Inject Environment Variables into Config where necessary (Overwrites)
# This maintains backward compatibility if specific ENV vars are used
if os.getenv("EMAIL_PASSWORD"):
    CONFIG["EMAIL"]["PASSWORD"] = os.getenv("EMAIL_PASSWORD")
if os.getenv("OPENAI_API_KEY"):
    CONFIG["LLM"]["API_KEY"] = os.getenv("OPENAI_API_KEY")
if os.getenv("LINKEDIN_EMAIL"):
    CONFIG["LINKEDIN"]["EMAIL"] = os.getenv("LINKEDIN_EMAIL")
if os.getenv("LINKEDIN_PASSWORD"):
    CONFIG["LINKEDIN"]["PASSWORD"] = os.getenv("LINKEDIN_PASSWORD")


def validate_config():
    """Validates the configuration for critical errors."""
    errors = []
    
    # Validate Scheduler
    if CONFIG["SCHEDULER"]["START_HOUR"] is not None and CONFIG["SCHEDULER"]["END_HOUR"] is not None:
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
