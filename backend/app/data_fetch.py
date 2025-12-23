from app.db_connection import get_db_connection

def fetch_customers():
    """Fetch customer data from the database."""
    connection = None
    try:
        # Establish connection to the database
        connection = get_db_connection()
        cursor = connection.cursor()

        # Execute query to fetch customers
        query = "SELECT * FROM customers;"
        cursor.execute(query)
        customers = cursor.fetchall()

        return customers

    except Exception as e:
        print(f"Error fetching customers: {e}")
        raise

    finally:
        # Close the connection
        if connection:
            cursor.close()
            connection.close()