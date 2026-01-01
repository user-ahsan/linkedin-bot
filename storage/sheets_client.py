import gspread
import csv
from oauth2client.service_account import ServiceAccountCredentials
from config.config import CONFIG
from core.logger import log_info, log_error, log_warn
import os
import json
import datetime

class SheetsClient:
    def __init__(self):
        self.client = None
        self.sheet = None
        self.interactions_ws = None
        self.profiles_ws = None
        self.offline_file = "storage/offline_data.json"
        
        # CSV Mirrors
        self.csv_interactions = "storage/interactions.csv"
        self.csv_profiles = "storage/profile_requests.csv"
        self._init_csvs()
        
        self.connected = False
        self._connect()
        
        # Try caching checks logic (sync)
        if self.connected:
            self.sync_offline_data()

    def _connect(self):
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds_file = CONFIG["GSPREAD"]["CREDENTIALS_FILE"]
            
            if not os.path.exists(creds_file):
                log_warn(f"Credentials file {creds_file} not found. Running in OFFLINE mode.", module="GUS")
                self.connected = False
                return

            creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
            self.client = gspread.authorize(creds)
            
            sheet_name = CONFIG["GSPREAD"]["SHEET_NAME"]
            try:
                self.sheet = self.client.open(sheet_name)
            except gspread.SpreadsheetNotFound:
                log_info(f"Spreadsheet '{sheet_name}' not found. Creating it...", module="GUS")
                self.sheet = self.client.create(sheet_name)
                # Share with TO email if possible
                to_email = CONFIG["EMAIL"].get("TO")
                if to_email and "your@email.com" not in to_email:
                    try:
                        self.sheet.share(to_email, perm_type='user', role='writer')
                    except Exception as share_err:
                        log_warn(f"Could not share sheet with {to_email}: {share_err}", module="GUS")
                
            # Get or create worksheets
            try:
                self.interactions_ws = self.sheet.worksheet("interactions")
            except:
                self.interactions_ws = self.sheet.add_worksheet(title="interactions", rows="1000", cols="5")
                self.interactions_ws.append_row(["Timestamp", "Action", "Target", "Status", "SessionID"])

            try:
                self.profiles_ws = self.sheet.worksheet("profile_requests_sent")
            except:
                self.profiles_ws = self.sheet.add_worksheet(title="profile_requests_sent", rows="1000", cols="7")
                self.profiles_ws.append_row(["Name", "Headline", "Skills", "URL", "Note", "Time", "Status"])

            log_info("Connected to Google Sheets successfully.", module="GUS")
            self.connected = True

        except Exception as e:
            log_error(f"Google Sheets Connection Failed: {e}. Switching to OFFLINE mode.", module="GUS")
            self.connected = False

    def _init_csvs(self):
        """Initialize CSV files with headers if they don't exist."""
        try:
            if not os.path.exists(self.csv_interactions):
                with open(self.csv_interactions, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Timestamp", "Action", "Target", "Status", "SessionID"])
            
            if not os.path.exists(self.csv_profiles):
                with open(self.csv_profiles, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Name", "Headline", "Skills", "URL", "Note", "Time", "Status"])
        except Exception as e:
            log_error(f"Failed to init CSVs: {e}", module="GUS")

    def _write_to_csv(self, filename, row):
        """Appends a row to the specified CSV file."""
        try:
             with open(filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
        except Exception as e:
             log_error(f"CSV Write Failed: {e}", module="GUS")

    def is_profile_processed(self, profile_url):
        """Checks if a profile URL already exists in the local CSV."""
        if not os.path.exists(self.csv_profiles): return False
        
        # Normalize input
        target_url = profile_url.split('?')[0].rstrip('/')
        
        try:
            with open(self.csv_profiles, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None) # Skip header
                for row in reader:
                    if len(row) > 3:
                        csv_url = row[3].split('?')[0].rstrip('/')
                        if csv_url == target_url:
                            return True
        except Exception as e:
            log_error(f"CSV Read Error: {e}", module="GUS")
        return False

    def _save_offline(self, type, data):
        """Saves data to a local JSON file."""
        entry = {
            "type": type,
            "data": data,
            "timestamp": str(datetime.datetime.now())
        }
        
        try:
            existing_data = []
            if os.path.exists(self.offline_file):
                with open(self.offline_file, 'r') as f:
                    try:
                        existing_data = json.load(f)
                    except json.JSONDecodeError:
                        pass # File might be corrupt or empty
            
            existing_data.append(entry)
            
            with open(self.offline_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
                
            log_info(f"Saved {type} to offline storage.", module="GUS")
        except Exception as e:
             log_error(f"Failed to save offline data: {e}", module="GUS")

    def sync_offline_data(self):
        """Attempts to upload offline data to Sheets."""
        if not os.path.exists(self.offline_file):
            return

        log_info("Syncing offline data to Sheets...", module="GUS")
        
        try:
            with open(self.offline_file, 'r') as f:
                data_list = json.load(f)
            
            remaining_data = []
            
            for item in data_list:
                success = False
                if item["type"] == "interaction":
                    success = self.append_interaction(item["data"], force_online=True)
                elif item["type"] == "profile_request":
                    # Reconstruct args logic
                    # Stored data is row list? 
                    # Wait, append_profile_request takes (profile_data, note, status)
                    # We should store args, or just store the formatted row.
                    # Current implementation below calls append_row directly.
                    # Optimally, _save_offline should store the raw arguments or the final row.
                    # Let's see how I implemented append_profile_request below.
                    # It constructs the row. 
                    # Let's enable passing 'row' directly or kwargs.
                    pass 
                    
                # NOTE: To simplify sync, I will modify append_* methods to just return Success status
                # And if they fail (when forcing online), we keep it.
                
                # Actually, simpler: 
                # Just fail fast. If connected, we are good.
                pass
                
            # For this iteration, let's keep it simple. 
            # If we are connected, we just wipe the file after processing? 
            # Or correct implementation:
            
            # Since I can't easily refactor the specialized arguments without changing the offline structure:
            # I will just clear the file if I'm connected for now to avoid complexity, 
            # OR better: I will implement specific sync logic if I have time. 
            # For now, let's just support saving.
            
            pass 
            
        except Exception as e:
            log_error(f"Sync failed: {e}", module="GUS")

    def append_interaction(self, row_data, force_online=False):
        # row_data: [timestamp, action, target, status, session_id]
        # Mirror to CSV always
        self._write_to_csv(self.csv_interactions, row_data)

        if self.connected:
            try:
                self.interactions_ws.append_row(row_data)
                return True
            except Exception as e:
                log_error(f"Failed to append interaction to Sheet: {e}", module="GUS")
                # Fallback to offline if connection dropped
                self._save_offline("interaction", row_data)
                return False
        else:
            self._save_offline("interaction", row_data)
            return True

    def append_profile_request(self, profile_data, note, status="SENT"):
        # Construct the row here
        import datetime
        row = [
            profile_data.get("name"),
            profile_data.get("headline"),
            ", ".join(profile_data.get("skills", [])[:5]),
            profile_data.get("url"),
            note,
            str(datetime.datetime.now()),
            status
        ]
            
        # Mirror to CSV always
        self._write_to_csv(self.csv_profiles, row)

        if self.connected:
            try:
                self.profiles_ws.append_row(row)
                return True
            except Exception as e:
                log_error(f"Failed to append profile request to Sheet: {e}", module="GUS")
                 # Fallback
                self._save_offline("profile_request_row", row)
                return False
        else:
             self._save_offline("profile_request_row", row)
             return True
             
    # Overriding sync for the row-based approach
    def sync_offline_data(self):
        if not os.path.exists(self.offline_file):
            return

        try:
            with open(self.offline_file, 'r') as f:
                data_list = json.load(f)
            
            if not data_list: return
            
            log_info(f"Found {len(data_list)} offline records. Syncing...", module="GUS")
            
            new_remaining = []
            for item in data_list:
                try:
                    if item["type"] == "interaction":
                        self.interactions_ws.append_row(item["data"])
                    elif item["type"] == "profile_request_row":
                        self.profiles_ws.append_row(item["data"])
                except Exception as e:
                    log_error(f"Sync failed for item: {e}", module="GUS")
                    new_remaining.append(item)
            
            # Retrieve remaining
            if len(new_remaining) < len(data_list):
                # Update file
                with open(self.offline_file, 'w') as f:
                    json.dump(new_remaining, f, indent=2)
                log_info("Sync complete.", module="GUS")
                
        except Exception as e:
             log_error(f"Critical Sync Error: {e}", module="GUS")
