# Configuration file for the project
from pathlib import Path
import os

# Resolve path relative to this file so it works regardless of CWD
_BASE_DIR = Path(__file__).resolve().parent
_DEFAULT_MODEL_PATH = _BASE_DIR / "artifacts" / "model_0.pkl"

# Allow overriding via environment variable MODEL_PATH
MODEL_PATH = os.getenv("MODEL_PATH", str(_DEFAULT_MODEL_PATH))