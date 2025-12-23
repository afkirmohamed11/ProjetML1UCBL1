import joblib
from config import MODEL_PATH

_model = None 

def load_model():
    print(MODEL_PATH)
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model

def get_model_info() -> dict:
    model = load_model()
    info = {
        "model_type": type(model).__name__,
        "feature_names": model.feature_names_in_.tolist() if hasattr(model, 'feature_names_in_') else [],
        "n_features": len(model.feature_names_in_) if hasattr(model, 'feature_names_in_') else 0,
    }
    return info

def process_input(data: dict) -> dict:
    """
    Process the input data to match the model's expected input format.
    This includes encoding categorical variables and scaling numerical features.
    """

    processed_data = {}

    # One-hot encode categorical features
    processed_data['internet_service_DSL'] = 1 if data['internet_service'] == 'DSL' else 0
    processed_data['internet_service_Fiber_optic'] = 1 if data['internet_service'] == 'Fiber optic' else 0
    processed_data['internet_service_No'] = 1 if data['internet_service'] == 'No' else 0

    processed_data['contract_One_year'] = 1 if data['contract'] == 'One year' else 0
    processed_data['contract_Two_year'] = 1 if data['contract'] == 'Two year' else 0
    processed_data['contract_Month_to_month'] = 1 if data['contract'] == 'Month-to-month' else 0

    processed_data['payment_method_Electronic_check'] = 1 if data['payment_method'] == 'Electronic check' else 0
    processed_data['payment_method_Mailed_check'] = 1 if data['payment_method'] == 'Mailed check' else 0
    processed_data['payment_method_Bank_transfer'] = 1 if data['payment_method'] == 'Bank transfer' else 0
    processed_data['payment_method_Credit_card'] = 1 if data['payment_method'] == 'Credit card' else 0

    # Copy boolean and numeric features directly
    for feature in ['senior_citizen', 'partner', 'dependents', 'online_security', 'tech_support', 'paperless_billing', 'monthly_charges', 'total_charges']:
        processed_data[feature] = data[feature]

    # Return the processed data as a dictionary
    return processed_data
