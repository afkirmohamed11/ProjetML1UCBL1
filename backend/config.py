# Configuration file for the project
from pathlib import Path
import os

# Resolve path relative to this file so it works regardless of CWD
_BASE_DIR = Path(__file__).resolve().parent
_DEFAULT_MODEL_PATH = _BASE_DIR / "artifacts" / "churn_pipeline.pkl"

# Allow overriding via environment variable MODEL_PATH
MODEL_PATH = os.getenv("MODEL_PATH", str(_DEFAULT_MODEL_PATH))

K_RETRAIN = int(os.getenv("K_RETRAIN", 20))  # example
COOLDOWN_MINUTES = int(os.getenv("COOLDOWN_MINUTES", 10))  # anti-boucle

# Service URLs
N8N_URL = os.getenv("N8N_URL", "http://n8n:5678")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")