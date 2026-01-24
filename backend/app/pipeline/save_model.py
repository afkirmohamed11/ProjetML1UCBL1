import joblib

def save_model(model, path):
    """
    Save the trained model to the specified path (generally within the artifacts directory).
    """
    joblib.dump(model, path)


#Example usage:from pipeline import build_pipeline
from train_pipeline import train_pipeline
pipeline = train_pipeline()
save_model(pipeline, "churn_pipeline.pkl")
