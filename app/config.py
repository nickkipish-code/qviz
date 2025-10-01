import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS = {int(x) for x in os.getenv("ADMINS", "").replace(" ", "").split(",") if x}
DB_URL = os.getenv("DB_URL", "sqlite+aiosqlite:///data.db")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Put it in your .env file.")
