import pandas as pd

def fetch_data_from_rds(table_name):

    RDS_HOST = "mlprojectdb.cx4k04y48cjc.eu-north-1.rds.amazonaws.com"
    RDS_PORT = 5432
    RDS_USER = "postgres"
    RDS_PASSWORD = "mlpipeline"
    RDS_DB_NAME = "telco_churn"
    TABLE_NAME = table_name
    
    # Création de l'URL de connexion avec psycopg2 explicite
    connection_url = f"postgresql+psycopg2://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}:{RDS_PORT}/{RDS_DB_NAME}"

    try:
        print("Connexion à RDS en cours...")
        # Requête SQL simple
        query = f"SELECT * FROM {TABLE_NAME}"
        
        # Passer directement l'URL de connexion à pandas (sans créer d'engine)
        ref_df = pd.read_sql_query(query, connection_url)
        
        print(f"Extraction réussie : {len(ref_df)} lignes de réf")
        return ref_df

    except Exception as e:
        print(f"Erreur lors de la connexion à RDS : {e}")
        return None
