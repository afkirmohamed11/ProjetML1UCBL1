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


def fetch_customer_by_id(customer_id: str):
    """Fetch a single customer by their ID and return a dict keyed by column names."""
    from decimal import Decimal

    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "SELECT * FROM customers WHERE customer_id = %s;"
        cursor.execute(query, (customer_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        # Map to dict using column names from cursor.description
        columns = [desc[0] for desc in cursor.description]
        data = dict(zip(columns, row))

        # Map notified_date to notified for frontend compatibility
        if 'notified_date' in data and 'notified' not in data:
            data['notified'] = data.get('notified_date', False)

        # Ensure status has a default value if None
        if data.get('status') is None or data.get('status') == '':
            data['status'] = 'not_notified'

        # Ensure JSON-serializable types (e.g., Decimal -> float)
        for k, v in list(data.items()):
            if isinstance(v, Decimal):
                data[k] = float(v)

        # Fetch latest prediction for this customer
        cursor.execute(
            """
            SELECT churn_score, churn_label, created_at 
            FROM predictions 
            WHERE customer_id = %s 
            ORDER BY created_at DESC 
            LIMIT 1
            """,
            (customer_id,)
        )
        prediction_row = cursor.fetchone()
        
        if prediction_row:
            data['churn_probability'] = float(prediction_row[0])
            data['churn_prediction'] = prediction_row[1]
            data['prediction_date'] = prediction_row[2].isoformat() if prediction_row[2] else None
        else:
            data['churn_probability'] = 0.0
            data['churn_prediction'] = False
            data['prediction_date'] = None

        return data

    except Exception as e:
        print(f"Error fetching customer by ID: {e}")
        raise

    finally:
        if connection:
            cursor.close()
            connection.close()


def fetch_customer_features(conn, customer_id: str) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT email, gender, senior_citizen, partner, dependents, tenure,
                   phone_service, multiple_lines, internet_service,
                   online_security, online_backup, device_protection, tech_support,
                   streaming_tv, streaming_movies, contract, paperless_billing,
                   payment_method, monthly_charges, total_charges
            FROM new_customers
            WHERE customer_id = %s
            """,
            (customer_id,)
        )
        row = cur.fetchone()
        if row is None:
            return None

        return {
            "customer_id": customer_id,
            "email": row[0],
            "gender": row[1],
            "senior_citizen": row[2],
            "partner": row[3],
            "dependents": row[4],
            "tenure": row[5],
            "phone_service": row[6],
            "multiple_lines": row[7],
            "internet_service": row[8],
            "online_security": row[9],
            "online_backup": row[10],
            "device_protection": row[11],
            "tech_support": row[12],
            "streaming_tv": row[13],
            "streaming_movies": row[14],
            "contract": row[15],
            "paperless_billing": row[16],
            "payment_method": row[17],
            "monthly_charges": float(row[18]) if row[18] is not None else None,
            "total_charges": float(row[19]) if row[19] is not None else None,
        }
