from app.model import load_model

def predict_churn(
        data: dict 
        ) -> float:
    model = load_model()

    # processed_data = process_input(data)   # Commented out after model refactor to process inside predict
    # Use raw data directly as processing is now inside the model

    # Make the prediction
    proba = model.predict_proba([data])[0][1]

    return float(proba)
