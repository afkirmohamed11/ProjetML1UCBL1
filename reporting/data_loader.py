import pandas as pd 
from model_loader import ModelLoader

class DataLoader:
    def __init__(self):
        self.preprocessor =  ModelLoader.load_model().named_steps['preprocess']
        self.customer_ref =  pd.read_csv("customer_ref.csv") 
        self.customer_prod =  pd.read_csv("customer_prod.csv") 

    def load_data(self):
        # Stocker les données avec le preprocessor
        prod_predictions = self.customer_prod["predictions"]
        ref_predictions = self.customer_ref["predictions"]
        prod_churn = self.customer_prod["churn"]
        ref_churn = self.customer_ref["churn"]
        self.customer_ref = self.customer_ref.drop('predictions', axis=1)
        self.customer_prod = self.customer_prod.drop('predictions', axis=1)

        # Transformer les données avec le preprocessor
        self.customer_ref = self.preprocessor.transform(self.customer_ref)
        self.customer_prod = self.preprocessor.transform(self.customer_prod)

        # Récuperer les predictions et les
        self.customer_prod["predictions"] = prod_predictions
        self.customer_ref["predictions"] = ref_predictions
        self.customer_prod["churn"]=prod_churn
        self.customer_ref["churn"]=ref_churn

        self.customer_prod["predictions"] = self.customer_prod["predictions"].map({False: 0, True: 1})
        self.customer_ref["predictions"] = self.customer_ref["predictions"].map({False: 0, True: 1})
        self.customer_prod["churn"] = self.customer_prod["churn"].map({False: 0, True: 1})
        self.customer_ref["churn"]  = self.customer_ref["churn"].map({False: 0, True: 1})

        return self.customer_ref, self.customer_prod    



def fetch_data_from_rds():

    RDS_HOST = "mlprojectdb.cx4k04y48cjc.eu-north-1.rds.amazonaws.com"
    RDS_PORT = 5432
    RDS_USER = "postgres"
    RDS_PASSWORD = "mlpipeline"
    RDS_DB_NAME = "telco_churn"
    TABLE_NAME = "prod_customers"
    
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
