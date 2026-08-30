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
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cf_coach.db")

# ── ChromaDB ──────────────────────────────────────────────────────────
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "cf_problems")

# ── Embedding Model ──────────────────────────────────────────────────
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# ── Auth / Sessions ──────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 days

# ── Codeforces API ───────────────────────────────────────────────────
CF_API_URL = "https://codeforces.com/api/problemset.problems"
