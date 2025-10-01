@echo off
    REM One-time install & env setup (Windows)
    python -m venv .venv
    call .\.venv\Scripts\activate.bat
    pip install -r requirements.txt
    if not exist ".env" copy .env.example .env
    echo.
    echo === Edit your .env (BOT_TOKEN, ADMINS) then run start.bat ===
    pause
