import boto3
import pickle
import logging
import pandas as pd
from sqlalchemy import create_engine, text

def put_model_in_s3(my_model):
    # 1. Setup your credentials
    ACCESS_KEY = '<access_key>'
    SECRET_KEY = '<secrect_key>'
    BUCKET_NAME = 'prodmodle'
    S3_FILE_PATH = 'production_model/champion.pkl'  # Where it will live in S3

    # 2. Create the S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )

    

    # 4. Serialize the model to bytes
    serialized_model = pickle.dumps(my_model)

    # 5. Upload to S3
    try:
        s3_client.put_object(Bucket=BUCKET_NAME, Key=S3_FILE_PATH, Body=serialized_model)
        logging.info(f"Successfully uploaded model to s3://{BUCKET_NAME}/{S3_FILE_PATH}")
    except Exception as e:
        logging.error(f"Error uploading to S3: {e}")

def update_customer_training_status():
    RDS_HOST = "mlprojectdb.cx4k04y48cjc.eu-north-1.rds.amazonaws.com"
    RDS_PORT = 5432
    RDS_USER = "postgres"
    RDS_PASSWORD = "mlpipeline"
    RDS_DB_NAME = "telco_churn"
    

    # Create the connection URL with explicit psycopg2
    connection_url = f"postgresql+psycopg2://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}:{RDS_PORT}/{RDS_DB_NAME}"
    engine = create_engine(connection_url)

    try:
        print("Connecting to RDS for update...")
        
        # Use a context manager to handle the connection and commit
        with engine.begin() as connection:
            # SQL query to update training status
            query = text("""
                UPDATE customers 
                SET ct_last_training = True 
                WHERE ct_last_training = False
            """)
            
            result = connection.execute(query)
            rows_affected = result.rowcount
            
        logging.info(f"Update successful: {rows_affected} rows modified.")
        logging.info(f"Success: {rows_affected} rows updated.")
        return rows_affected

    except Exception as e:
        logging.error(f"UPDATE Error: {e}")
        return None