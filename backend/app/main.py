from fastapi import FastAPI
from app.schemas import PredictRequest, PredictResponse
from app.predict import predict_churn
from app.model import get_model_info
from app.data_fetch import fetch_customers

app = FastAPI(title="Telco Churn Prediction API")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest):
    """Endpoint to predict customer churn probability."""
    proba = predict_churn(payload.dict())
    return {"churn_probability": proba}


@app.get("/model_info")
def model_info():
    """Return metadata about the loaded model to help integration."""
    return get_model_info()


@app.get("/customers")
def get_customers():
    """Endpoint to fetch customer data."""
    try:
        customers = fetch_customers()
        return {"customers": customers}
    except Exception as e:
        return {"error": str(e)}
