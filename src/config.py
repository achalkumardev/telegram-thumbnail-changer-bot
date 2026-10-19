import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

# Attempt loading .env from project root first, then src directory, then default environment
if (ROOT_DIR / ".env").is_file():
    load_dotenv(ROOT_DIR / ".env")
elif (BASE_DIR / ".env").is_file():
    load_dotenv(BASE_DIR / ".env")
else:
    load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()
BOT_NAME: str = os.getenv("BOT_NAME", "Thumbnail Changer Bot").strip()
API_ID_RAW = os.getenv("API_ID", "").strip()
API_HASH: str = os.getenv("API_HASH", "").strip()

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is required. Please set it in your .env file (see .env.example).")

API_ID: int = int(API_ID_RAW) if API_ID_RAW else 0
ADMIN_ID_RAW = os.getenv("ADMIN_ID", "7437014244").strip()
ADMIN_ID: int = int(ADMIN_ID_RAW) if ADMIN_ID_RAW.isdigit() else 7437014244
