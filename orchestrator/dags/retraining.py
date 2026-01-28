from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import logging
import mlflow
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.train_finetune  import  model_retraining
from src.model_evaluation import model_evaluation
from src.model_deployement  import deploy_model

# ----add pipeline path to import it during unpickling
pipeline_path = os.path.abspath('/opt/airflow/src/utils')  # Use absolute path
if pipeline_path not in sys.path:
    sys.path.insert(0, pipeline_path)  # Use insert(0) to prioritize
    print(f"Added path to: {pipeline_path}")


    



with DAG(
    dag_id='ml_retraining_pipeline',
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,  # IMPORTANT : None signifie qu'il attend un trigger (API ou manuel)
    catchup=False,
    tags=['mlops', 'retraining']
) as dag:

    task_retraining = PythonOperator(
        task_id='model_retraining_task',
        python_callable=model_retraining
    )

    task_evaluation = PythonOperator(
        task_id='model_evaluation_task',
        python_callable=model_evaluation
    )

    task_deployment = PythonOperator(
        task_id='model_depolyment',
        python_callable=deploy_model
    )

    task_retraining >> task_evaluation >> task_deployment