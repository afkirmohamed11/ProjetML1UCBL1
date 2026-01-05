import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection parameters
RDS_HOST = os.getenv("RDS_HOST")
RDS_PORT = os.getenv("RDS_PORT", 5432)  # Default PostgreSQL port
RDS_DB_NAME = os.getenv("RDS_DB_NAME")
RDS_USER = os.getenv("RDS_USER")
RDS_PASSWORD = os.getenv("RDS_PASSWORD")

def get_db_connection():
    """Establish and return a database connection."""
    try:
        print('Establishing database connection...')
        connection = psycopg2.connect(
            host=RDS_HOST,
            port=RDS_PORT,
            database=RDS_DB_NAME,
            user=RDS_USER,
            password=RDS_PASSWORD
        )
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise

def ensure_customers_table(conn):
    """Create the customers table if it does not exist (superset schema)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                customer_id        TEXT PRIMARY KEY,
                gender             TEXT,
                senior_citizen     BOOLEAN,
                partner            BOOLEAN,
                dependents         BOOLEAN,
                tenure             INTEGER,

                phone_service      BOOLEAN,
                multiple_lines     TEXT,

                internet_service   TEXT,
                online_security    TEXT,
                online_backup      TEXT,
                device_protection  TEXT,
                tech_support       TEXT,
                streaming_tv       TEXT,
                streaming_movies   TEXT,

                contract            TEXT,
                paperless_billing   BOOLEAN,
                payment_method      TEXT,

                monthly_charges     NUMERIC(10,2),
                total_charges       NUMERIC(10,2),

                churn               BOOLEAN,
                status              VARCHAR(20),
                notified            BOOLEAN,
                updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                first_name          VARCHAR(50),
                last_name           VARCHAR(50),
                email               VARCHAR(100)
            )
            """
        )
