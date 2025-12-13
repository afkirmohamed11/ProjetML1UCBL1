from app.model import load_model

def predict_churn(
        data: dict # TODO: specify the input based on schema
        ) -> float:
    model = load_model()

    # TODO: use the model to make a prediction
    proba = 0.0  

    return float(proba)
