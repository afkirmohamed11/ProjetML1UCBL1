import pandas as pd
import psycopg2
from psycopg2 import sql

def read_postgres_table(dbname, user, password, host, port, table_name):
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
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Example usage
# df = read_postgres_table("mydb", "myuser", "mypassword", "localhost", 5432, "mytable")
# print(df.head())
