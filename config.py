import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
# Load environment variables from .env if present
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()
BOT_NAME: str = os.getenv("BOT_NAME", "Thumbnail Changer Bot").strip()
API_ID_RAW = os.getenv("API_ID", "").strip()
API_HASH: str = os.getenv("API_HASH", "").strip()

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is required. Please set it in your .env file (see .env.example).")

API_ID: int = int(API_ID_RAW) if API_ID_RAW else 0
