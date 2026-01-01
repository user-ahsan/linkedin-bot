import os
import datetime
import sys

# Define log levels
INFO = "INFO"
WARN = "WARN"
ERROR = "ERROR"
FATAL = "FATAL"

LOG_DIR = "logs"
LOG_FILE = "bot.log"

def _ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

def log(level, message, module="CORE"):
    _ensure_log_dir()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Format: [TIMESTAMP] [LEVEL] [MODULE] - Message
    formatted_msg = f"[{timestamp}] [{level}] [{module}] - {message}"
    
    # Print to terminal with basic colors (using ANSI escape codes)
    color = ""
    reset = "\033[0m"
    if level == INFO:
        color = "\033[94m" # Blue
    elif level == WARN:
        color = "\033[93m" # Yellow
    elif level == ERROR:
        color = "\033[91m" # Red
    elif level == FATAL:
        color = "\033[41m" # Red Background
        
    print(f"{color}{formatted_msg}{reset}")
    
    # Append to log file
    log_path = os.path.join(LOG_DIR, LOG_FILE)
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(formatted_msg + "\n")
    except Exception as e:
        print(f"FAILED TO WRITE LOG: {e}")

def log_info(msg, module="CORE"):
    log(INFO, msg, module)

def log_warn(msg, module="CORE"):
    log(WARN, msg, module)

def log_error(msg, module="CORE"):
    log(ERROR, msg, module)

def log_fatal(msg, module="CORE"):
    log(FATAL, msg, module)
    # Fatal events might imply an exit, but we leave that to the caller
