from mlflow import MlflowClient
import pandas as pd
from sklearn.model_selection import GridSearchCV, train_test_split
from src.utils.build_pipeline import build_pipeline
from src.utils.data_manager import fetch_data_from_rds 
import logging
import mlflow



def task_tune_and_train(train_customers):
    # Initialize variables to None to avoid UnboundLocalError
    reg_result = None
    grid = None
    
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("Churn_Retraining_Experiment")
    
    mlflow.sklearn.autolog(
        log_input_examples=True,
        log_model_signatures=True
    )

    try:
        with mlflow.start_run(run_name="grid_search_tuning") as run:
            # 1. Prepare Data
            # Check for NaN values here! If build_pipeline handles them, you're fine.
            X = train_customers.drop(columns=["churn"])
            y = train_customers["churn"]

            # 2. Build and Fit
            pipeline = build_pipeline()
            
            param_grid = {
                'model__C': [0.01, 0.1, 1, 10],
                'model__penalty': ['l1', 'l2'],
                'model__solver': ['liblinear', 'saga']
            }

            grid = GridSearchCV(
                estimator=pipeline, 
                param_grid=param_grid, 
                scoring='recall', 
                cv=5, 
                n_jobs=-1,
                refit=True 
            )
            
            # This is where your sample mismatch [4616, 4636] is occurring
            grid.fit(X, y)

            # 3. Register Model
            model_uri = f"runs:/{run.info.run_id}/model"
            reg_result = mlflow.register_model(
                model_uri=model_uri,
                name="churn_model"
            )
            
            return {
                "status": "success",
                "model_version": reg_result.version,
                "best_recall": grid.best_score_,
                "run_id": run.info.run_id
            }

    except Exception as e:
        logging.error(f"Training failed: {e}")
        # Return a failure state instead of letting 'finally' crash the script
        return {
            "status": "failed",
            "error": str(e),
            "model_version": None,
            "best_recall": 0
        }
    

def model_retraining(**kwargs):

    # fetch the data from RDS
    customers = fetch_data_from_rds()
    customers.drop_duplicates(inplace=True)

    customers.drop(columns=["customer_id","predictions"], inplace=True)

    #select the new and old customers
    new_customers = customers[customers['ct_last_training'] == False]
    old_customers = customers[customers['ct_last_training'] == True]

    new_customers.drop(columns=["ct_last_training"], inplace=True)
    old_customers.drop(columns=["ct_last_training"], inplace=True)

    #shuffle the new customers
    new_customers = new_customers.sample(frac=1, random_state=42)

    #split the new customers into two parts: 80% for training and 20% for testing
    eval_model_customers = new_customers[:int(new_customers.shape[0]*.2)]
    new_customers = new_customers[int(new_customers.shape[0]*.2):]
    #Store the eval_model_customers into RDS table model_eval
    # new_customers.to_parquet("new_customers.parquet", index=False)
    # insert_dataframe_into_rds(eval_model_customers,"model_eval")



    train_customers = pd.concat([old_customers[int(old_customers.shape[0]*0.7):], new_customers])

    results = task_tune_and_train(train_customers)

    kwargs['ti'].xcom_push(key='training_results', value=results)
    kwargs['ti'].xcom_push(key='eval_model_customers', value=eval_model_customers.to_dict())


