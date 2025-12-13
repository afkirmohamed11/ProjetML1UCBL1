import pandas as pd
import psycopg2
# from dotenv import load_dotenv
import os

def read_postgres_table():
    """
    Reads a PostgreSQL table and returns it as a Pandas DataFrame.

    Parameters:
        dbname (str): Database name
        user (str): Username
        password (str): Password
        host (str): Host (e.g., 'localhost')
        port (int/str): Port (e.g., 5432)
        table_name (str): Name of the table to read

    Returns:
        pd.DataFrame: Data from the table
    """
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )
    
    # Build query as a string safely
    query = f'SELECT * FROM "{os.getenv("TABLE_NAME")}"' 
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# Example usage
# Load environment variables from .env file
# load_dotenv()

# df = read_postgres_table()
# print(df.head())
