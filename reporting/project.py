import os
import pandas as pd
import json
from sqlalchemy import create_engine
from evidently import Report, Dataset, BinaryClassification, DataDefinition
from evidently.presets import DataDriftPreset, ClassificationPreset
from evidently.ui.workspace import Workspace
from data_loader import DataLoader,fetch_data_from_rds

def extract_metrics_from_report(my_eval, customer_prod, customer_ref):
    """Extrait les métriques du rapport Evidently et les sauvegarde pour Prometheus."""
    
    # Charger les métriques
    metrics = json.loads(my_eval.json())["metrics"]
    
    # Dictionnaire pour stocker les résultats
    results = {
        "drift_scores": {},
        "global_drift": {},
        "classification": {},
        "data_info": {}
    }
    
    # Parcourir toutes les métriques
    for metric in metrics:
        metric_name = metric.get("metric_name", "")
        config = metric.get("config", {})
        value = metric.get("value")
        
        # 1. Extraire les drifts des colonnes spécifiques
        if "ValueDrift" in metric_name:
            column = config.get("column", "")
            if column in ["payment_method_Electronic_check", "internet_service_Fiber_optic", 
                         "monthly_charges", "paperless_billing"]:
                results["drift_scores"][column] = value
        
        # 2. Extraire le drift global
        elif "DriftedColumnsCount" in metric_name:
            results["global_drift"]["nombre_colonnes_driftees"] = value.get("count")
            results["global_drift"]["share_colonnes_driftees"] = value.get("share")
        
        # 3. Extraire les métriques de classification
        elif "Accuracy" in metric_name:
            results["classification"]["accuracy"] = value
        elif "Precision" in metric_name and "ByLabel" not in metric_name:
            results["classification"]["precision"] = value
        elif "Recall" in metric_name and "ByLabel" not in metric_name:
            results["classification"]["recall"] = value
        elif "F1Score" in metric_name and "ByLabel" not in metric_name:
            results["classification"]["f1_score"] = value
    
    # 4. Informations sur les données
    results["data_info"] = {
        "nombre_enregistrements_current": len(customer_prod),
        "nombre_enregistrements_reference": len(customer_ref),
        "nombre_colonnes": len(customer_prod.columns)
    }
    
    print("Métriques extraites du rapport Evidently")
    return results


def create_report():
    ws = Workspace.create("workspace")
    
    # Création ou récupération du projet
    existing_projects = ws.search_project("Churn Monitoring")
    if not existing_projects:
        project = ws.create_project("Churn Monitoring")
    else:
        project = existing_projects[0]

    # data_loader = DataLoader()
    customers = fetch_data_from_rds()
    customer_prod = customers[customers["ct_Last_training"] == False]
    customer_ref = customers[customers["ct_Last_training"] == True]
    customer_ref.drop(["ct_Last_training"], axis=1, inplace=True)
    customer_prod.drop(["ct_Last_training"], axis=1, inplace=True)
    # ================================================================================
    # 1. Prepare your column lists
    # Exclude the ones you don't want to analyze for drift
    excluded_cols = ['customer_id', 'predictions']

    # Get all other columns
    all_features = [c for c in customer_prod.columns if c not in excluded_cols]

    # Separate them by type so Evidently uses the correct statistical test
    # Numerical: float64 and int64 (like tenure, monthly_charges)
    num_cols = customer_prod[all_features].select_dtypes(include=['number']).columns.tolist()

    # Categorical: object, bool, and category (like gender, partner, contract)
    cat_cols = customer_prod[all_features].select_dtypes(exclude=['number']).columns.tolist()
    # ================================================================================================================


    # 2. Update the DataDefinition
    definition = DataDefinition(
        # Explicitly map features
        numerical_columns=num_cols,
        categorical_columns=cat_cols,
        
        # Define the ML task targets
        classification=[BinaryClassification(
            target="churn",
            prediction_labels="predictions"
        )]
    )

    # 3. Create the datasets as you did before
    current_data = Dataset.from_pandas(customer_prod, data_definition=definition)
    reference_data = Dataset.from_pandas(customer_ref, data_definition=definition)

    # Créer et exécuter le rapport
    report = Report(metrics=[
        DataDriftPreset(),
        ClassificationPreset(),
    ])

    my_eval = report.run(reference_data=reference_data, current_data=current_data)

    # Ajout du run au workspace
    ws.add_run(project.id, my_eval, include_data=False)
    print("Nouveau rapport généré avec succès.")
    
    # Extraire et sauvegarder les métriques pour Prometheus
    metrics = extract_metrics_from_report(my_eval, customer_prod, customer_ref)
    
    return metrics


if __name__ == "__main__":
    # create_report()
    df = fetch_data_from_rds()
    print(df.head(2))