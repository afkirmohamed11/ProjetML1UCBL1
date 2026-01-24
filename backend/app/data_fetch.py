from app.db_connection import get_db_connection

def fetch_customers():
    """Fetch customer data with their predictions and feedback status."""
    from decimal import Decimal
    
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        print('Fetching customers with predictions and feedback from database...')
        
        # Join customers with latest predictions and feedback - only essential fields
        query = """
            SELECT 
                c.customer_id,
                c.first_name,
                c.last_name,
                c.email,
                c.contract,
                c.monthly_charges,
                c.total_charges,
                p.churn_label,
                p.created_at as prediction_date,
                f.sent_at as notified_date,
                f.answered_at as feedback_date,
                f.answer as feedback_answer
            FROM customers c
            LEFT JOIN LATERAL (
                SELECT churn_label, created_at
                FROM predictions
                WHERE customer_id = c.customer_id
                ORDER BY created_at DESC
                LIMIT 1
            ) p ON true
            LEFT JOIN LATERAL (
                SELECT sent_at, answered_at, answer
                FROM feedback
                WHERE prediction_id IN (
                    SELECT prediction_id 
                    FROM predictions 
                    WHERE customer_id = c.customer_id 
                    ORDER BY created_at DESC 
                    LIMIT 1
                )
                ORDER BY answered_at DESC
                LIMIT 1
            ) f ON true
            ORDER BY c.customer_id;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Convert rows to list of dicts
        customers = []
        for row in rows:
            data = dict(zip(columns, row))
            
            # Convert Decimal to float for JSON serialization
            for k, v in list(data.items()):
                if isinstance(v, Decimal):
                    data[k] = float(v)
            
            customers.append(data)

        return customers

    except Exception as e:
        print(f"Error fetching customers: {e}")
        raise

    finally:
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

        # Fetch latest prediction and feedback for this customer
        cursor.execute(
            """
            SELECT 
                p.prediction_id,
                p.churn_score, 
                p.churn_label, 
                p.created_at,
                f.feedback_id,
                f.answer,
                f.used_for_training,
                f.answered_at
            FROM predictions p
            LEFT JOIN feedback f ON f.prediction_id = p.prediction_id
            WHERE p.customer_id = %s 
            ORDER BY p.created_at DESC 
            LIMIT 1
            """,
            (customer_id,)
        )
        prediction_row = cursor.fetchone()
        
        if prediction_row:
            data['prediction_id'] = prediction_row[0]
            data['churn_probability'] = float(prediction_row[1]) if prediction_row[1] else 0.0
            data['churn_prediction'] = prediction_row[2]
            data['prediction_date'] = prediction_row[3].isoformat() if prediction_row[3] else None
            data['feedback_id'] = prediction_row[4]
            data['feedback_answer'] = prediction_row[5]
            data['used_for_training'] = prediction_row[6]
            data['feedback_date'] = prediction_row[7].isoformat() if prediction_row[7] else None
        else:
            data['prediction_id'] = None
            data['churn_probability'] = 0.0
            data['churn_prediction'] = False
            data['prediction_date'] = None
            data['feedback_id'] = None
            data['feedback_answer'] = None
            data['used_for_training'] = None
            data['feedback_date'] = None

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
