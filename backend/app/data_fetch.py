from app.db_connection import get_db_connection

def fetch_customers():
    """Fetch customer data from the database."""
    connection = None
    try:
        # Establish connection to the database
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Execute query to fetch customers
        print('Fetching customers from database...')
        query = "SELECT * FROM customers limit 10;"
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


def fetch_customer_by_id(customer_id: str):
    """Fetch a single customer by their ID."""
    connection = None
    try:
        # Establish connection to the database
        connection = get_db_connection()
        cursor = connection.cursor()

        # Execute query to fetch the customer by ID
        query = "SELECT * FROM customers WHERE customer_id = %s;"
        cursor.execute(query, (customer_id,))
        customer = cursor.fetchone()

        return customer

    except Exception as e:
        print(f"Error fetching customer by ID: {e}")
        raise

    finally:
        # Close the connection
        if connection:
            cursor.close()
            connection.close()