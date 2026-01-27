import os
import pandas as pd
import json
from sqlalchemy import create_engine
from evidently import Report, Dataset, BinaryClassification, DataDefinition
from evidently.presets import DataDriftPreset, ClassificationPreset
from evidently.ui.workspace import Workspace
from data_loader import DataLoader

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
    
    print("✓ Métriques extraites du rapport Evidently")
    return results


def create_report():
    ws = Workspace.create("workspace")
    
    # Création ou récupération du projet
    existing_projects = ws.search_project("Churn Monitoring")
    if not existing_projects:
        project = ws.create_project("Churn Monitoring")
    else:
        project = existing_projects[0]
    
    data_loader = DataLoader()
    customer_ref, customer_prod = data_loader.load_data()

    # Configuration de la définition des données
    definition = DataDefinition(
        classification=[BinaryClassification(
            target="churn",
            prediction_labels="predictions"
        )],
        categorical_columns=customer_prod.select_dtypes(include=['int64']).columns.tolist()
    )

    # Créer les Dataset objects
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
    print("✓ Nouveau rapport généré avec succès.")
    
    # Extraire et sauvegarder les métriques pour Prometheus
    metrics = extract_metrics_from_report(my_eval, customer_prod, customer_ref)
    
    return metrics


if __name__ == "__main__":
    create_report()