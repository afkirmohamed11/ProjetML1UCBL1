import os
import pandas as pd
from sqlalchemy import create_engine
from evidently import Report, Dataset, BinaryClassification, DataDefinition
from evidently.presets import DataDriftPreset, ClassificationPreset
from evidently.ui.workspace import Workspace
from data_loader import DataLoader

def create_report():
    ws = Workspace.create("workspace")
    
    # Création ou récupération du projet
    existing_projects = ws.search_project("Churn Monitoring")
    if not existing_projects:
        project = ws.create_project("Churn Monitoring")
    else:
        project = existing_projects[0]

    # Configuration de la définition des données
    definition = DataDefinition(
        classification=[BinaryClassification(
            target="churn",                      # Vraies valeurs
            prediction_labels="predictions"      # Prédictions du modèle
        )],
        categorical_cols = customer_prod.select_dtypes(include=['int64']).columns.tolist()
    )
    data_loader = DataLoader()

    customer_ref, customer_prod = data_loader.load_data()

    # Créer les Dataset objects
    current_data = Dataset.from_pandas(customer_prod, data_definition=definition)
    reference_data = Dataset.from_pandas(customer_ref, data_definition=definition)
    
    # Créer et exécuter le rapport
    report = Report(metrics=[
        DataDriftPreset(),
        ClassificationPreset(),
    ])
    
    my_eval = report.run(reference_data=reference_data, current_data=current_data)
    
    # Ajout du run au workspace (pas add_report mais add_run)
    ws.add_run(project.id, my_eval, include_data=False)
    print("✓ Nouveau rapport généré avec succès.")


if __name__ == "__main__":
    create_report()