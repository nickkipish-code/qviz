\
    # Telegram Bot with Admin Panel (Windows quick start)

    ## 1) Requirements
    - Python 3.11+ (recommended 3.12)
    - Telegram bot token from @BotFather

    ## 2) Setup on Windows (PowerShell)
    ```powershell
    cd <folder-you-unzipped>
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    copy .env.example .env
    # edit .env and set BOT_TOKEN + your numeric Telegram ID in ADMINS
    python -m app.main
    ```

    ## 3) Commands
    - `/start` — shows the main menu (reply keyboard).
    - `/admin` — admin panel (only for IDs listed in `ADMINS`).

    ## Notes
    - Database is SQLite file `data.db` in project root.
    - If `/admin` does not open, ensure your numeric ID is in `ADMINS` and restart the bot.
    - To stop: press `Ctrl+C` in the console.
