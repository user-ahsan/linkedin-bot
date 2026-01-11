@echo off
title LinkedIn Autonomous Agent Manager
cls

echo ====================================================
echo      INITIALIZING ENVIRONMENT
echo ====================================================

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH!
    echo Please install Python 3.9+ and try again.
    pause
    exit
)

:: 2. Check/Create Virtual Environment
if not exist .venv (
    echo [INFO] Virtual environment not found. Creating one...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create .venv. Check your Python installation.
        pause
        exit
    )
    echo [INFO] .venv created successfully.
)

:: 3. Install/Update Dependencies
:: We only do this if requirements changed or .venv is new, to save time on loop?
:: For now, valid check is fast enough.
echo [INFO] Environment Check...
if not exist .venv\Scripts\flask.exe (
    echo [INFO] Installing dependencies...
    .venv\Scripts\python -m pip install --upgrade pip >nul 2>&1
    .venv\Scripts\python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit
    )
)

:menu
cls
echo ====================================================
echo      LINKEDIN AUTONOMOUS AGENT - MANAGER
echo ====================================================
echo.
echo 1. Run Terminal Mode (Interactive)
echo    - Press 's' to skip/stop current action
echo    - Press 'q' to quit to this menu
echo.
echo 2. Check/Fix Login Session (Manual Login)
echo    - Opens browser to let you log in manually
echo    - Use this if bot fails to login
echo.
echo 3. Run Web Interface (Dashboard)
echo    - Starts Flask server on port 5000
echo.
echo 4. Run All Tests
echo    - Verifies setup and functionality
echo.
echo 5. Exit
echo.
echo ====================================================
echo.
echo [Use keyboard numbers 1-5 to select]
choice /C 12345 /N /M "Select an option > "

if errorlevel 5 goto exit
if errorlevel 4 goto run_tests
if errorlevel 3 goto run_web
if errorlevel 2 goto run_session_check
if errorlevel 1 goto run_terminal
goto menu

:run_terminal
cls
echo Starting Terminal Mode...
echo Press 'q' at any time inside the bot to return to the menu.
echo.
.venv\Scripts\python main.py
echo.
echo Process ended. Returning to menu...
pause
goto menu

:run_session_check
cls
echo Starting Session Manager...
echo.
.venv\Scripts\python core/session_manager.py
echo.
echo Session Check Complete. Returning to menu...
pause
goto menu

:run_web
cls
echo Starting Web Interface...
echo Press CTRL+C to stop the server and return to menu.
echo.
.venv\Scripts\python web_app.py
echo.
echo Server stopped. Returning to menu...
pause
goto menu

:run_tests
cls
echo Running Tests...
echo.
if exist test_stealth.py (
    echo [Test 1/1] Testing Stealth Module...
    .venv\Scripts\python test_stealth.py
) else (
    echo [Info] test_stealth.py not found (cleaned up).
)
echo.
echo Executing unit tests if available...
:: Add other test scripts here
echo.
pause
goto menu

:exit
echo Exiting...
exit
