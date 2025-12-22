import joblib
from config import MODEL_PATH

_model = None 

def load_model():
    print(MODEL_PATH)
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
        # Compatibility shim for older pickled sklearn models
        try:
            from sklearn.linear_model import LogisticRegression
            if isinstance(_model, LogisticRegression) and not hasattr(_model, "multi_class"):
                # Default behavior in modern sklearn is 'auto'
                _model.multi_class = "auto"
        except Exception:
            # If sklearn isn't available or model isn't LogisticRegression, skip silently
            pass
    return _model

