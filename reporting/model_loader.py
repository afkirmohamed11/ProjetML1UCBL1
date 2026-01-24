import joblib
import os
import sys

# Ajouter le chemin du module pipeline pour permettre l'import lors du unpickling
pipeline_path = os.path.abspath('./artifacts')
if pipeline_path not in sys.path:
    sys.path.append(pipeline_path)
    print(f"Chemin ajouté au sys.path: {pipeline_path}")

class ModelLoader:
    model = None
    model_path = './artifacts/churn_pipeline.pkl'

    @classmethod
    def load_model(cls):

        # Charger le modèle
        if os.path.exists(cls.model_path):
            print(f"Chargement du modèle depuis: {cls.model_path}")
            cls.model = joblib.load(cls.model_path)
            print(f"Modèle chargé avec succès!")
            return cls.model
        else:
            print(f"Fichier non trouvé: {cls.model_path}")
            print("Vérifiez le chemin du modèle.")
            return None