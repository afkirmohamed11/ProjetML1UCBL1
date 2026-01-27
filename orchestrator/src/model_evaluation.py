import logging
import mlflow
import pandas as pd
from sklearn.metrics import recall_score


def model_evaluation (**kwargs):

    mlflow.set_tracking_uri("http://mlflow:5000")

    # retreive the payloads from XCom
    results = kwargs['ti'].xcom_pull(key='training_results', task_ids='model_retraining_task')
    eval_model_customers_dict = kwargs['ti'].xcom_pull(key='eval_model_customers', task_ids='model_retraining_task')
    eval_model_customers = pd.DataFrame.from_dict(eval_model_customers_dict)
    logging.info("Starting model evaluation...")
    logging.info(f"results: {results}")
    logging.info(f"eval_model_customers: {eval_model_customers.head()}")


    # prepare the test data
    X_test = eval_model_customers.drop(["churn"],axis=1)
    y_test = eval_model_customers["churn"]

    #retrieve the challenger model from mlflow reistery
    challenger_uri = f"models:/churn_model/{results['model_version']}"
    challenger_model = mlflow.sklearn.load_model(challenger_uri)

    #retrieve the champion model from mlflow reistery
    champion_uri = f"models:/churn_model@champion"
    champion_model = mlflow.sklearn.load_model(champion_uri)

    # evaluate the challenger model
    y_pred_challenger = challenger_model.predict(X_test)
    recall_challenger = recall_score(y_test, y_pred_challenger)
    logging.info(f"Challenger Recall: {recall_challenger:.4f}")

    # evaluate the champion model
    y_pred_champion = champion_model.predict(X_test)
    recall_champion = recall_score(y_test, y_pred_champion)
    logging.info(f"Champion Recall: {recall_champion:.4f}")



    if recall_challenger > recall_champion:
        logging.info("The challenger model outperforms the champion model. Promoting challenger to champion.")
        #promote the challenger model to champion
        client = mlflow.tracking.MlflowClient()
        client.set_registered_model_alias("churn_model", "champion", results['model_version'])
        logging.info(f" Modèle version {results['model_version']} promu au statut CHAMPION")
    else:
        logging.info("The champion model remains the best model. No changes made.")
    

   

