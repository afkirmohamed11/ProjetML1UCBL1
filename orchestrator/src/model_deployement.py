from src.utils.s3_manager import update_customer_training_status, put_model_in_s3
import mlflow
import logging


def deploy_model(**kwargs):

    changed = kwargs['ti'].xcom_pull(key='changed', task_ids='model_evaluation_task')

    if changed:
        mlflow.set_tracking_uri("http://mlflow:5000")
        #retrieve the champion model from mlflow reistery

        champion_uri = f"models:/churn_model@champion"
        champion_model = mlflow.sklearn.load_model(champion_uri)
        put_model_in_s3(champion_model)

    try:
        update_customer_training_status()
        logging.info("update data successfuly")
    except Exception as e:
        logging.error(f"ERROR occured: {e}")






