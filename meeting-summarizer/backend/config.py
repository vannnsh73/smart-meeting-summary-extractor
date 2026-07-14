"""
Centralized configuration - loads all env vars in one place.
"""
import os
from dotenv import load_dotenv

load_dotenv(override=True)

OPENROUTER_API_KEY: str = os.environ.get("OPENROUTER_API_KEY", "")
SENDGRID_API_KEY: str = os.environ.get("SENDGRID_API_KEY", "")
SENDGRID_FROM_EMAIL: str = os.environ.get("SENDGRID_FROM_EMAIL", "")

if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY is not set in .env")
