from playwright.sync_api import sync_playwright
from config.config import CONFIG
from core.logger import log_info, log_error, log_fatal
import sys
import os

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.context = None
        self.page = None

    def launch_browser(self):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                log_info(f"Launching Browser (Attempt {attempt+1}/{max_retries})...")
                self.playwright = sync_playwright().start()
                
                user_data_dir = CONFIG["BROWSER"]["USER_DATA_DIR"]
                full_user_data_dir = os.path.abspath(user_data_dir)
                
                headless_mode = CONFIG["BROWSER"]["HEADLESS"]
                
                # Cleanup Profile Locks (Fix for "Target page closed" errors if related to profile locking)
                try:
                    lock_file = os.path.join(full_user_data_dir, "SingletonLock")
                    socket_file = os.path.join(full_user_data_dir, "SingletonSocket")
                    if os.path.exists(lock_file):
                        os.remove(lock_file)
                    if os.path.exists(socket_file):
                        os.remove(socket_file)
                except Exception as cleanup_err:
                    print(f"Warning: Could not clean up profile locks: {cleanup_err}")

                # Stealth Arguments
                stealth_args = [
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--excludeSwitches=enable-automation",
                    "--use-fake-ui-for-media-stream",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-extensions",
                    "--disable-popup-blocking",
                ]

                # Using launch_persistent_context to maintain login session
                self.context = self.playwright.chromium.launch_persistent_context(
                    user_data_dir=full_user_data_dir,
                    headless=headless_mode,
                    channel="chrome", # Try to use installed chrome or default
                    args=stealth_args,
                    viewport=None, # Uses actual window size
                    timeout=30000,
                    ignore_default_args=["--enable-automation"]  # Crucial for hiding automation bar
                )
                
                # Apply Stealth Scripts
                self.context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                # Get the first page or create new one
                if len(self.context.pages) > 0:
                    self.page = self.context.pages[0]
                else:
                    self.page = self.context.new_page()
                    
                log_info("Browser launched successfully.")
                return self.page
                
            except Exception as e:
                log_error(f"Failed to launch browser on attempt {attempt+1}: {e}")
                if self.playwright:
                    try:
                        self.playwright.stop()
                    except:
                        pass
                if attempt == max_retries - 1:
                    log_fatal("All browser launch attempts failed.")
                    raise e
                import time
                time.sleep(5) # Wait before retry

    def close_browser(self):
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()
        log_info("Browser closed.")
    
    def get_page(self):
        return self.page
