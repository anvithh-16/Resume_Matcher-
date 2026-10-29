import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parents[2]
APP_ENV = os.getenv("APP_ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", "./storage"))
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", "2097152"))
TOKEN_MINUTES = int(os.getenv("TOKEN_MINUTES", "60"))
EXTERNAL_AI_ENABLED = os.getenv("EXTERNAL_AI_ENABLED", "false").lower() == "true"

if APP_ENV == "production" and SECRET_KEY == "dev-only-secret":
    raise RuntimeError("Set a real SECRET_KEY before running in production.")
