import time
from prometheus_client import start_http_server, Gauge
from project import create_report
import traceback
import logging
from airflow_trigger import send_trigger

# === PROMETHEUS GAUGES (Renamed with _g to avoid variable collision) ===
share_drift_g = Gauge('drift_share', 'Pourcentage de colonnes qui ont drifté')
number_drift_g = Gauge('drift_count', 'Nombre absolu de colonnes qui ont drifté')

# Drift par colonne
drift_payment_electronic_g = Gauge('payment_method_Electronic_check_drift', 'Drift Electronic check')
drift_internet_fiber_g = Gauge('internet_service_Fiber_optic_drift', 'Drift Fiber optic')
drift_monthly_charges_g = Gauge('monthly_charges_drift', 'Drift monthly charges')
drift_paperless_billing_g = Gauge('paperless_billing_drift', 'Drift paperless billing')

# Classification
accuracy_g = Gauge('accuracy', 'Model accuracy')
precision_g = Gauge('precision', 'Model precision')
recall_g = Gauge('recall', 'Model recall')
f1_score_g = Gauge('f1_score', 'Model F1 score')

# Data Info
current_data_count_g = Gauge('current_data_count', 'Nombre enregistrements prod')
reference_data_count_g = Gauge('reference_data_count', 'Nombre enregistrements ref')
columns_count_g = Gauge('columns_count', 'Nombre total de colonnes')

def update_metrics_from_evidently():
    try:
        print("\n Génération d'un nouveau rapport Evidently...")
        metrics = create_report()
        evaluation_metrics = {}  
        
        if 'global_drift' in metrics:
            nombre = metrics['global_drift'].get('nombre_colonnes_driftees', 0)
            share = metrics['global_drift'].get('share_colonnes_driftees', 0)
            number_drift_g.set(nombre)
            share_drift_g.set(share)
            evaluation_metrics['share_drifted_columns'] = share

        if 'drift_scores' in metrics:
            ds = metrics['drift_scores']
            drift_payment_electronic_g.set(ds.get('payment_method_Electronic_check', 0))
            drift_internet_fiber_g.set(ds.get('internet_service_Fiber_optic', 0))
            drift_monthly_charges_g.set(ds.get('monthly_charges', 0))
            drift_paperless_billing_g.set(ds.get('paperless_billing', 0))
            
            # Key names synced with your main loop requirements
            evaluation_metrics['payment_method_Electronic_check'] = ds.get('payment_method_Electronic_check', 0)
            evaluation_metrics['internet_service_Fiber_optic'] = ds.get('internet_service_Fiber_optic', 0)
            evaluation_metrics['monthly_charges'] = ds.get('monthly_charges', 0)
            evaluation_metrics['paperless_billing'] = ds.get('paperless_billing', 0)

        if 'classification' in metrics:
            cl = metrics['classification']
            accuracy_g.set(cl.get('accuracy', 0))
            precision_g.set(cl.get('precision', 0))
            recall_g.set(cl.get('recall', 0))
            f1_score_g.set(cl.get('f1_score', 0))
            evaluation_metrics['recall'] = cl.get('recall', 0)
        
        if 'data_info' in metrics:
            di = metrics['data_info']
            logging.info("di: %s", di)
            nb_current = di.get('nombre_enregistrements_current', 0)
            current_data_count_g.set(nb_current)
            reference_data_count_g.set(di.get('nombre_enregistrements_reference', 0))
            columns_count_g.set(di.get('nombre_colonnes', 0))
            evaluation_metrics['nb_current'] = nb_current
        
        logging.info(" Métriques Prometheus mises à jour!")
        return evaluation_metrics

    except Exception as e:
        logging.error(" Erreur: %s", e)
        traceback.print_exc()
        return {} # Returns empty dict so .get() calls don't crash the loop

if __name__ == '__main__':
    start_http_server(8020)
    
    while True:
        evaluation_metrics = update_metrics_from_evidently()
        
        # We use your exact variable names for the alert logic
        rec_count = evaluation_metrics.get('nb_current', 0)
        recall = evaluation_metrics.get('recall', 0)
        share_drifted_columns = evaluation_metrics.get('share_drifted_columns', 0)  
        payment_method_Electronic_check = evaluation_metrics.get('payment_method_Electronic_check', 0)
        internet_service_Fiber_optic = evaluation_metrics.get('internet_service_Fiber_optic', 0)
        monthly_charges = evaluation_metrics.get('monthly_charges', 0)
        paperless_billing = evaluation_metrics.get('paperless_billing', 0)

        # Your original Alert Logic maintained
        if rec_count >= 200 and (recall < 0.8 or share_drifted_columns > 0.5 or
           payment_method_Electronic_check > 0.3 or internet_service_Fiber_optic > 0.3 or 
           monthly_charges > 0.3 or paperless_billing > 0.3):
            
            send_trigger()
            time.sleep(600)
        else:
            logging.info(" No alert detected !")

        time.sleep(10) # Updated to 5 minutes as requested
    

    