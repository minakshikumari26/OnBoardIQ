"""
Central configuration for OnBoardIQ.

Env vars are loaded from a local .env file (git-ignored) if present.
Anything not set in .env falls back to the defaults below.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# ── Database ──────────────────────────────────────────────────────────────────
DB_NAME     = os.getenv("DB_NAME",     "loan_db")
DB_USER     = os.getenv("DB_USER",     "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "0921")
DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = os.getenv("DB_PORT",     "5432")

# ── LLM (Groq) ────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL    = "llama-3.3-70b-versatile"

# ── External services ─────────────────────────────────────────────────────────
OPENSANCTIONS_API_URL = "https://api.opensanctions.org/search/default"
OPENSANCTIONS_TIMEOUT = 5   # seconds
