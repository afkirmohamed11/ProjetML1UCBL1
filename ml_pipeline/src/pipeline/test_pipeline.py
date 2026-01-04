from pathlib import Path
import pandas as pd
import joblib

BASE_DIR = Path(__file__).resolve().parents[2]  # src/
PIPELINE_PATH = BASE_DIR / "artifacts" / "churn_pipeline.pkl"

def build_test_dataframe():
    return pd.DataFrame([
        {
            "customer_id": "0001-A",
            "gender": "Male",
            "senior_citizen": False,
            "partner": True,
            "dependents": False,
            "tenure": 12,
            "phone_service": True,
            "multiple_lines": "Yes",
            "internet_service": "Fiber optic",
            "online_security": "No",
            "online_backup": "Yes",
            "device_protection": "No",
            "tech_support": "No",
            "streaming_tv": "Yes",
            "streaming_movies": "Yes",
            "contract": "Month-to-month",
            "paperless_billing": True,
            "payment_method": "Electronic check",
            "monthly_charges": 89.50,
            "total_charges": 1023.75,
            "churn": False,   # optional for predict
            "status": "responded_ok",
            "notified": True,
            "updated_at": "2024-01-15 10:00:00",
            "first_name": "Mariam",
            "last_name": "Al-Hussein",
            "email": "mariam.al-hussein@outlook.com"
        }
    ])


def main():
    pipeline = joblib.load(PIPELINE_PATH)

    df = build_test_dataframe()

    # Drop target for inference
    X = df.drop(columns=["churn"])

    preds = pipeline.predict(X)
    probs = pipeline.predict_proba(X)

    print("Predictions:", preds)
    print("Probabilities:", probs)


if __name__ == "__main__":
    main()
