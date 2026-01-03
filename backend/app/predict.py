from app.model import load_model
import pandas as pd

def predict_churn(
        data: dict 
        ) -> float:
    model = load_model()

    # processed_data = process_input(data)   # Commented out after model refactor to process inside predict
    # Use raw data directly as processing is now inside the model

    # Make the prediction
    data = pd.DataFrame([data])
    data.drop(columns=['churn', 'email'], inplace=True, errors='ignore')
    proba = model.predict_proba(data)[0][1]

    return float(proba)
