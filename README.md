# LinkedIn Autonomous Engagement Agent

A safe, human-like autonomous agent for ongoing LinkedIn engagement. This bot runs on your machine, manages its own state, and performs actions like scrolling the feed, visiting profiles, and sending connection requests with personalized notes (optional).

## 🚀 Key Features

- **Auto-Login & Recovery**: Automatically logs in using credentials if session expires. Detects and handles casual logouts.
- **Human-like Behavior**: Random delays, natural scrolling, and probabilistic actions to avoid detection.
- **Safety First**: strict rate limits, active hours enforcement, and automatic shutdown on CAPTCHA detection.
- **Privacy Focused**: Runs locally on your machine. No credentials are sent to third parties.
- **Configurable**: Easily adjust daily limits, working hours, and feature toggles.
- **Integrated**:
    - **OpenAI/ChatGPT**: Customized connection notes (optional).
    - **Google Sheets**: Logs all interactions and sent requests (optional).
    - **Email Alerts**: Notifies you if the bot gets blocked or crashes (optional).

## 🛠 Prerequisites

- **Python 3.10+** installed on your system.
- **Chrome** browser installed.
- (Optional) **OpenAI API Key** for smart notes.
- (Optional) **Google Service Account Credentials** (`credentials.json`) for Sheets logging.
- (Optional) **Gmail App Password** for email alerts.

## 📦 Installation

1.  **Clone/Download** this repository.
2.  **Setup Environment**:
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Linux/Mac:
    source .venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```

4.  **Setup Credentials**:
    - Create a `.env` file in the root (or rename `.env.example` if provided).
    - Add your LinkedIn credentials for auto-login:
      ```env
      LINKEDIN_EMAIL=your_email@example.com
      LINKEDIN_PASSWORD=your_password
      ```
    - Add other keys (OPENAI_API_KEY, etc.) as needed.

5.  **Setup Configuration**:
    - Open `config/config.py`.
    - You can edit the settings directly or use a `.env` file.
    - **Important**: To enable "Use Headless Mode" (invisible browser), set `HEADLESS: True`. Default is `False`.

## ⚙️ Configuration Guide

The `config/config.py` file controls everything. Here are the key sections:

### 1. Browser Settings
```python
"BROWSER": {
    "HEADLESS": False,  # Set to True to hide the browser window
    "USER_DATA_DIR": "./browser_profile" # Where cookies/session are saved
}
```

### 2. Limits & Schedule
```python
"LIMITS": {
    "LIKES_PER_DAY": 45,
    "CONNECTIONS_PER_DAY": 12
},
"SCHEDULER": {
    "START_HOUR": 9,   # Set to None to run 24/7 (Ignore time limits)
    "END_HOUR": 18
}
```
*To test if the bot works immediately, you can set `START_HOUR: None` in `config.py`.*

### 3. Smart Notes (OpenAI)
If you want the bot to write personalized notes:
1.  Set your `OPENAI_API_KEY` in environment variables or config.
2.  Ensure `ENABLE_SMART_NOTES` is `True` (default).

**Fallback behavior**: If no API key is provided, the bot will automatically **disable smart notes** and send standard connection requests ("Send without note") instead. It will NOT fail.

### 4. Search Keywords
Add the job titles or keywords you want to target in `inputs/searchpeople.txt`, one per line:
```text
Software Engineer
Recruiter
Product Manager
```

### 5. Offline Storage & Google Sheets
- **Offline Mode**: If `credentials.json` is missing or the internet is down, the bot **saves data locally** to `storage/offline_data.json`.
- **Auto-Sync**: When the bot restarts with a working Sheets connection, it automatically uploads the offline data to Google Sheets.
- **Auto-Create**: If your sheet doesn't exist, the bot creates it for you (and shares it with your email if configured).

## ▶️ Usage

1.  **Run the Bot**:
    ```bash
    python main.py
    ```

2.  **First Run (Manual Login)**:
    - The browser will open.
    - **Log in to LinkedIn manually**.
    - Once logged in, close the terminal (Ctrl+C) and restart the bot.
    - Your session is now saved in `./browser_profile`.

3.  **Deployment**:
    - You can leave this running in a terminal.
    - It will sleep at night and wake up in the morning automatically.
    - If you are on a server, look into using `pm2` or `systemd` to keep it running in the background.

## ⚠️ Safety & Disclaimers

- **CAPTCHA**: The bot attempts to detect CAPTCHAs. If detected, it **STOPS immediately** and sends an alert. **Do not attempt to bypass CAPTCHAs automatically.**
- **Rate Limits**: Start conservative. Do not increase limits aggressively.
- **Responsibility**: You are responsible for your LinkedIn account. Use this tool ethically and reasonably.

## ❓ Troubleshooting

- **"No module named pip"**: Run `python -m ensurepip --default-pip` in your terminal.
- **Bot keeps sleeping**: Check `config.py` timezone and active hours. It might be night time in the configured timezone.
- **Google Sheets Error**: Ensure `credentials.json` is in the root folder and the permissions are correct.

