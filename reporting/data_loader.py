import pandas as pd 
from model_loader import ModelLoader
class DataLoader:
    def __init__(self):
        self.preprocessor =  ModelLoader.load_model().named_steps['preprocess']
        self.customer_ref =  pd.read_csv("customer_ref.csv") 
        self.customer_prod =  pd.read_csv("customer_drift.csv") 

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