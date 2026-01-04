import time
from prometheus_client import start_http_server, Gauge
from project import create_report

# === MÉTRIQUES DE DRIFT GLOBAL ===
# nombre_colonnes_driftees = nombre ABSOLU de colonnes qui ont drifté (ex: 3 colonnes)
share_drifted_columns = Gauge('drift_share', 
                              'Pourcentage de colonnes qui ont drifté (ex: 0.15 = 15%)')
number_drifted_columns = Gauge('drift_count', 
                               'Nombre absolu de colonnes qui ont drifté (ex: 3)')

# === MÉTRIQUES DE DRIFT PAR COLONNE SPÉCIFIQUE ===
# Noms exacts des colonnes avec suffixe _drift
drift_payment_electronic = Gauge('payment_method_Electronic_check_drift', 
                                 'Drift score for payment_method_Electronic_check')
drift_internet_fiber = Gauge('internet_service_Fiber_optic_drift', 
                             'Drift score for internet_service_Fiber_optic')
drift_monthly_charges = Gauge('monthly_charges_drift', 
                              'Drift score for monthly_charges')
drift_paperless_billing = Gauge('paperless_billing_drift', 
                                'Drift score for paperless_billing')

# === MÉTRIQUES DE CLASSIFICATION ===
accuracy_gauge = Gauge('accuracy', 'Model accuracy')
precision_gauge = Gauge('precision', 'Model precision')
recall_gauge = Gauge('recall', 'Model recall')
f1_score_gauge = Gauge('f1_score', 'Model F1 score')

# === MÉTRIQUES D'INFORMATION SUR LES DONNÉES ===
current_data_count = Gauge('current_data_count', 
                           'Nombre d\'enregistrements dans les données de production (current)')
reference_data_count = Gauge('reference_data_count', 
                             'Nombre d\'enregistrements dans les données de référence')
columns_count = Gauge('columns_count', 
                      'Nombre total de colonnes dans les datasets')

def update_metrics_from_evidently():
    """Appelle directement create_report() pour obtenir les métriques Evidently."""
    
    try:
        print("\n Génération d'un nouveau rapport Evidently...")
        metrics = create_report()
        
        # Mettre à jour le drift global
        if 'global_drift' in metrics:
            nombre = metrics['global_drift'].get('nombre_colonnes_driftees', 0)
            share = metrics['global_drift'].get('share_colonnes_driftees', 0)
            number_drifted_columns.set(nombre)
            share_drifted_columns.set(share)
            print(f"   Drift global: {nombre} colonnes ({share*100:.1f}%)")
        
        # Mettre à jour les drifts par colonne
        if 'drift_scores' in metrics:
            drift_scores = metrics['drift_scores']
            drift_payment_electronic.set(drift_scores.get('payment_method_Electronic_check', 0))
            drift_internet_fiber.set(drift_scores.get('internet_service_Fiber_optic', 0))
            drift_monthly_charges.set(drift_scores.get('monthly_charges', 0))
            drift_paperless_billing.set(drift_scores.get('paperless_billing', 0))
            print(f"   {len(drift_scores)} drifts de colonnes spécifiques extraits")
        
        # Mettre à jour les métriques de classification
        if 'classification' in metrics:
            classification = metrics['classification']
            accuracy_gauge.set(classification.get('accuracy', 0))
            precision_gauge.set(classification.get('precision', 0))
            recall_gauge.set(classification.get('recall', 0))
            f1_score_gauge.set(classification.get('f1_score', 0))
            print(f"   Accuracy: {classification.get('accuracy', 0):.4f}")
            print(f"   F1 Score: {classification.get('f1_score', 0):.4f}")
        
        # Mettre à jour les informations sur les données
        if 'data_info' in metrics:
            data_info = metrics['data_info']
            nb_current = data_info.get('nombre_enregistrements_current', 0)
            nb_ref = data_info.get('nombre_enregistrements_reference', 0)
            nb_cols = data_info.get('nombre_colonnes', 0)
            
            current_data_count.set(nb_current)
            reference_data_count.set(nb_ref)
            columns_count.set(nb_cols)
            
            print(f"   Données PROD (current): {nb_current} enregistrements")
            print(f"   Données REF: {nb_ref} enregistrements")
            print(f"   {nb_cols} colonnes au total")
        
        print("\n Métriques Prometheus mises à jour avec succès!")
        
    except Exception as e:
        print(f"\n Erreur lors de la mise à jour des métriques: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # Démarrer le serveur HTTP pour Prometheus sur le port 8020
    start_http_server(8020)
    print("=" * 70)
    print("🚀 SERVEUR DE MÉTRIQUES PROMETHEUS DÉMARRÉ")
    print("=" * 70)
    print("📍 Port: 8020")
    print("🌐 Métriques: http://localhost:8020/metrics")
    print("🔄 Mise à jour: toutes les 5 minutes (300 secondes)")
    print("📊 Source: Appel direct de create_report() dans project.py")
    print("=" * 70)
    print("\n📋 MÉTRIQUES EXPOSÉES:")
    print("  • current_data_count - Nombre d'enregistrements PROD")
    print("  • reference_data_count - Nombre d'enregistrements REF")
    print("  • drift_count - Nombre de colonnes driftées")
    print("  • drift_share - % de colonnes driftées")
    print("  • payment_method_Electronic_check_drift - Drift colonne spécifique")
    print("  • internet_service_Fiber_optic_drift - Drift colonne spécifique")
    print("  • monthly_charges_drift - Drift colonne spécifique")
    print("  • paperless_billing_drift - Drift colonne spécifique")
    print("  • accuracy - Précision du modèle")
    print("  • precision - Précision du modèle")
    print("  • recall - Rappel du modèle")
    print("  • f1_score - Score F1")
    print("=" * 70)
    # print("=" * 70)
    # print("📍 Port: 8000")
    # print("🌐 Métriques: http://localhost:8000/metrics")
    # print("🔄 Mise à jour: toutes les 5 minutes (300 secondes)")
    # print("📊 Source: Appel direct de create_report() dans project.py")
    # print("=" * 70)
    # print("\n📋 MÉTRIQUES EXPOSÉES:")
    # print("  • evidently_current_data_count - Nombre d'enregistrements PROD")
    # print("  • evidently_reference_data_count - Nombre d'enregistrements REF")
    # print("  • evidently_number_drifted_columns - Nombre de colonnes driftées")
    # print("  • evidently_share_drifted_columns - % de colonnes driftées")
    # print("  • evidently_accuracy - Précision du modèle")
    # print("  • evidently_f1_score - Score F1")
    # print("=" * 70)
    
    # Boucle infinie pour mettre à jour les métriques
    while True:
        update_metrics_from_evidently()
        print(f"\n⏳ Prochain rapport dans 5 minutes...\n")
        time.sleep(300)  # Mise à jour toutes les 5 minutes