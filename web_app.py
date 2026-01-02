import os
import signal
import subprocess
import sys
import time
import json
from flask import Flask, render_template, jsonify, request, Response

# Add project root to path so we can import config if needed (though we use json primarily)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import CONFIG_FILE, load_config, save_config

import logging
# Disable Werkzeug access logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

# Global variable to hold the bot process
BOT_PROCESS = None
LOG_FILE = os.path.join("logs", "bot.log")

def get_last_logs(n=50):
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return lines[-n:]
    except Exception as e:
        return [f"Error reading logs: {e}"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status")
def status():
    global BOT_PROCESS
    is_running = BOT_PROCESS is not None and BOT_PROCESS.poll() is None
    return jsonify({"running": is_running, "pid": BOT_PROCESS.pid if is_running else None})

@app.route("/api/start", methods=["POST"])
def start_bot():
    global BOT_PROCESS
    if BOT_PROCESS is not None and BOT_PROCESS.poll() is None:
        return jsonify({"status": "error", "message": "Bot is already running"}), 400
    
    # Run main.py using the same python executable
    try:
        # Use python from the current environment
        python_exe = sys.executable 
        cmd = [python_exe, "main.py"]
        
        # Open in new console? No, we want to capture output or let it log to file.
        # Since main.py logs to file, we can just spawn it.
        # We redirect stdout/stderr to devnull or let it inherit to the web app console?
        # Ideally, main.py writes to logs/bot.log.
        
        BOT_PROCESS = subprocess.Popen(cmd, cwd=os.getcwd())
        return jsonify({"status": "success", "message": "Bot started", "pid": BOT_PROCESS.pid})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/stop", methods=["POST"])
def stop_bot():
    global BOT_PROCESS
    if BOT_PROCESS is None or BOT_PROCESS.poll() is not None:
        return jsonify({"status": "error", "message": "Bot is not running"}), 400
    
    try:
        BOT_PROCESS.terminate()
        # Give it a moment to die gracefully
        try:
            BOT_PROCESS.wait(timeout=5)
        except subprocess.TimeoutExpired:
            BOT_PROCESS.kill()
            
        BOT_PROCESS = None
        return jsonify({"status": "success", "message": "Bot stopped"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/logs")
def get_logs():
    lines = get_last_logs(100)
    return jsonify({"logs": lines})

@app.route("/api/config", methods=["GET"])
def get_config():
    conf = load_config()
    return jsonify(conf)

@app.route("/api/config", methods=["POST"])
def update_config():
    new_conf = request.json
    if save_config(new_conf):
        return jsonify({"status": "success", "message": "Config saved"})
    else:
        return jsonify({"status": "error", "message": "Failed to save config"}), 500

if __name__ == "__main__":
    # Completely disable Werkzeug logging to keep terminal clean
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    log.disabled = True
    app.logger.disabled = True
    
    # Run without debug mode if possible to minimize noise, or keep it but with logs silenced
    print("\n" + "="*60)
    print(" 🤖 LINKEDIN BOT WEB INTERFACE IS READY")
    print(" 👉 Open Dashboard: http://localhost:5000")
    print("    (Hold Ctrl + Click the link above to open)")
    print("="*60 + "\n")
    print("Press Ctrl+C to stop the server.")
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
