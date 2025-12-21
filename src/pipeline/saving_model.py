import joblib
# import sys
# from pathlib import Path
# from dotenv import load_dotenv
# load_dotenv()
# BASE_DIR = Path(__file__).resolve().parent.parent.parent
# sys.path.append(str(BASE_DIR / 'src'))

# from pipeline.preprocess import preprocess_data
# from pipeline.model_training import train_logistic_model

def save_model(model, path):
    """
    Save the trained model to the specified path (generally within the artifacts directory).
    """
    joblib.dump(model, path)


# BASE_DIR = Path(__file__).resolve().parent.parent.parent

# if __name__ == '__main__':
#     # use the preprocessing pipeline to get a cleaned, numeric DataFrame
#     df = preprocess_data()
#     model = train_logistic_model(df)

#     model_path = BASE_DIR / 'artifacts' / 'logistic_regression_model.pkl'
#     save_model(model, model_path)