from app.model import load_model

def predict_churn(
        data: dict # TODO: specify the input based on schema
        ) -> float:
    model = load_model()

    # TODO: use the model to make a prediction
    features = model.feature_names_in_
    X = [data[name] for name in features]
    proba = model.predict_proba([X])[0][1]

    return float(proba)
