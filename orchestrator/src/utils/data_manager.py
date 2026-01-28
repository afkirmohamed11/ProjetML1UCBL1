import pandas as pd
import logging

<<<<<<< HEAD


def fetch_data_from_rds():
=======
def fetch_data_from_rds(table_name):
>>>>>>> bdf381eaa88b4939ca2fdf2d4d6c2e390f0a072a

    RDS_HOST = "mlprojectdb.cx4k04y48cjc.eu-north-1.rds.amazonaws.com"
    RDS_PORT = 5432
    RDS_USER = "postgres"
    RDS_PASSWORD = "mlpipeline"
    RDS_DB_NAME = "telco_churn"
<<<<<<< HEAD
    TABLE_NAME = "prod_customers"
=======
    TABLE_NAME = table_name
>>>>>>> bdf381eaa88b4939ca2fdf2d4d6c2e390f0a072a
    
    # Création de l'URL de connexion avec psycopg2 explicite
    connection_url = f"postgresql+psycopg2://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}:{RDS_PORT}/{RDS_DB_NAME}"

    try:
        print("Connexion à RDS en cours...")
        # Requête SQL simple
<<<<<<< HEAD
        query = f"""SELECT 
                    c.customer_id, 
                    c.gender, 
                    c.senior_citizen, 
                    c.partner, 
                    c.dependents,
                    c.tenure, 
                    c.phone_service, 
                    c.multiple_lines, 
                    c.internet_service,
                    c.online_security, 
                    c.online_backup, 
                    c.device_protection, 
                    c.tech_support,
                    c.streaming_tv, 
                    c.streaming_movies, 
                    c.contract, 
                    c.paperless_billing,
                    c.payment_method, 
                    c.monthly_charges, 
                    c.total_charges, 
                    c.ct_last_training,
                    p.churn_label AS predictions,
                    f.answer AS churn  -- Raw data from feedback table
                FROM customers AS c
                INNER JOIN predictions AS p 
                    ON c.customer_id = p.customer_id
                INNER JOIN feedback AS f 
                    ON p.prediction_id = f.prediction_id
                WHERE p.churn_label IS NOT NULL 
                AND f.answer IS NOT NULL;"""
        
        # Passer directement l'URL de connexion à pandas (sans créer d'engine)
        ref_df = pd.read_sql_query(query, connection_url)
        ref_df["churn"] = ref_df["churn"].map({
                                'YES': True, 
                                'yes': True, 
                                'NO': False, 
                                'no': False
                            }).astype(bool)
        print(f"Extraction réussie : {len(ref_df)} lignes de réf")
=======
        query = f"SELECT * FROM {TABLE_NAME}"
        
        # Passer directement l'URL de connexion à pandas (sans créer d'engine)
        ref_df = pd.read_sql_query(query, connection_url)
        
        logging.info(f"Extraction réussie : {len(ref_df)} lignes de réf")
>>>>>>> bdf381eaa88b4939ca2fdf2d4d6c2e390f0a072a
        return ref_df

    except Exception as e:
        print(f"Erreur lors de la connexion à RDS : {e}")
        return None
<<<<<<< HEAD



=======
>>>>>>> bdf381eaa88b4939ca2fdf2d4d6c2e390f0a072a
