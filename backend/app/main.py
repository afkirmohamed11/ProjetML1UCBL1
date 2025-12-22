from fastapi import FastAPI
from app.schemas import PredictRequest, PredictResponse
from app.predict import predict_churn
from app.info import get_model_info

app = FastAPI(title="Telco Churn Prediction API")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest):
    proba = predict_churn(payload.dict())
    return {"churn_probability": proba}


@app.get("/model_info")
def model_info():
    """Return metadata about the loaded model to help integration."""
    return get_model_info()
