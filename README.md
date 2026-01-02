# LinkedIn Autonomous Engagement Agent

A safe, human-like autonomous agent for ongoing LinkedIn engagement. This bot runs on your machine, manages its own state, and performs actions like scrolling the feed, visiting profiles, and sending connection requests with personalized notes (optional).

**NEW: Now includes a full Web Interface for easy control and configuration!**

## 🚀 Key Features

- **Web Control Panel**: Start/Stop the bot, view live logs, and edit configuration from a beautiful web dashboard.
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
    - Create a `.env` file in the root.
    - Add your LinkedIn credentials:
      ```env
      LINKEDIN_EMAIL=your_email@example.com
      LINKEDIN_PASSWORD=your_password
      ```

## ▶️ Usage (Web Interface)

The recommended way to use the bot is via the new Web Interface.

1.  **Start the Web App**:
    ```bash
    python web_app.py
    ```

2.  **Open Dashboard**:
    - Go to [http://localhost:5000](http://localhost:5000) in your browser.

3.  **Control & Configure**:
    - **Start/Stop**: Use the big buttons to control the bot process.
    - **Live Logs**: Watch the bot's activities in real-time.
    - **Configuration**: Scroll down to the Configuration section to edit settings (Speed, Limits, Headless Mode, etc.). Click **Save Config** to apply changes immediately (restart bot to take effect).

## ⚙️ Configuration Guide

Configuration is now stored in `config/config.json` and can be edited via the Web Interface.

### Key Settings
- **BROWSER.HEADLESS**: Set to `true` to run the bot invisibly, or `false` to see the browser.
- **LIMITS**: Set daily limits for likes, visits, and connections.
- **SCHEDULER**: Define `START_HOUR` and `END_HOUR` to simulate working hours. Set `START_HOUR` to `null` to run 24/7.
- **SEARCH_SETTINGS**: Configure how deep the bot searches and filters.

### Smart Notes (OpenAI)
To enable AI-generated connection notes:
1.  Enter your `OPENAI_API_KEY` in the Web Config (under `LLM` section) or `.env` file.
2.  Ensure `ENABLE_SMART_NOTES` is `true`.

### Search Keywords
Add job titles or keywords to target in `inputs/searchpeople.txt`, one per line:
```text
Software Engineer
Recruiter
Product Manager
```

## ⚠️ Safety & Disclaimers

- **CAPTCHA**: The bot attempts to detect CAPTCHAs. If detected, it **STOPS immediately**.
- **Result Scanning**: The bot uses intelligent scanning to find "Connect" buttons.
- **Responsibility**: You are responsible for your LinkedIn account. Use this tool ethically.

## ❓ Troubleshooting

- **Web App fails to start**: Ensure you installed `flask` and `python-dotenv`: `pip install -r requirements.txt`.
- **Bot logic errors**: Check the "Live Logs" on the dashboard.
