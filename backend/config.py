"""
Centralized configuration — reads from .env and exposes constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same directory as this file
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path, override=True)

# ── Database URL (supports both PostgreSQL and SQLite) ────────────────
_default_database_path = (Path(__file__).resolve().parent / "cf_coach.db").as_posix()
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_default_database_path}")

# ── ChromaDB ──────────────────────────────────────────────────────────
_default_chroma_path = Path(__file__).resolve().parent / "chroma_data"
_chroma_path = Path(os.getenv("CHROMA_PERSIST_DIR", str(_default_chroma_path)))
if not _chroma_path.is_absolute():
    _chroma_path = Path(__file__).resolve().parent / _chroma_path
CHROMA_PERSIST_DIR = str(_chroma_path.resolve())
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "cf_problems")

# ── This instance is dedicated to one Codeforces profile ──────────────
CF_PROFILE_HANDLE = "vaibhavreddy"
CF_PROFILE_NAME = "Vaibhav Reddy"
CF_PROFILE_URL = f"https://codeforces.com/profile/{CF_PROFILE_HANDLE}"

# ── Auth / Sessions ──────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 days

# ── Codeforces API ───────────────────────────────────────────────────
CF_API_URL = "https://codeforces.com/api/problemset.problems"
