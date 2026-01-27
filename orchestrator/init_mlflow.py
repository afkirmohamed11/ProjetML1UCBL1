import mlflow
import joblib
from mlflow.tracking import MlflowClient
import os
import sys


# Ajouter le chemin du module pipeline pour permettre l'import lors du unpickling
mlflow.set_tracking_uri("http://mlflow:5000")
pipeline_path = os.path.abspath('./artifacts')
if pipeline_path not in sys.path:
    sys.path.append(pipeline_path)
    print(f"Chemin ajouté au sys.path: {pipeline_path}")

def init_champion_model(pkl_path, model_name="my_model"):
    client = MlflowClient()
    
    # --- FIX: Check if the model already exists ---
    try:
        latest_versions = client.get_latest_versions(model_name)
        
        if latest_versions:
            print(f"⚠️ Model '{model_name}' already exists (Version {latest_versions[0].version}). Skipping initialization.")
            return # Exit function early so no new run is created
    except Exception:
        print(f"Model '{model_name}' not found. Initializing for the first time...")

    # 1. Charger le modèle
    model = joblib.load(pkl_path)
    
    # 2. Créer une run MLflow
    with mlflow.start_run(run_name="initial_champion_run") as run:
        mlflow.sklearn.log_model(model, "model", registered_model_name=model_name)
        
        # 3. Récupérer la version 1 et mettre l'alias
        client.set_registered_model_alias(model_name, "champion", "1")
        print(f"✅ Modèle initial enregistré sous version 1 et tagué CHAMPION")

if __name__ == '__main__':
    init_champion_model("./artifacts/churn_pipeline.pkl", model_name="churn_model")