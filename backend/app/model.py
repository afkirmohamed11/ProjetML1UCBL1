import joblib
from backend.config import MODEL_PATH

_model = None 

def load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model

