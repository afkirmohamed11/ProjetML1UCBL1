from app.model import load_model, process_input

def predict_churn(
        data: dict 
        ) -> float:
    model = load_model()

    processed_data = process_input(data)
    features = model.feature_names_in_
    X = [processed_data[name] for name in features]

    # Make the prediction
    proba = model.predict_proba([X])[0][1]

    return float(proba)
