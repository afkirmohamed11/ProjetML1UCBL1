from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import PredictInput, PredictRequest, PredictResponse
from app.predict import predict_churn
from app.model import get_model_info
from app.data_fetch import fetch_customers, fetch_customer_by_id, fetch_customer_features
from uuid import uuid4
from app.db_connection import get_db_connection, ensure_customers_table
from psycopg2.errors import UniqueViolation
from app.schemas import FeedbackRequest, FeedbackResponse, RetrainRequest, CustomerDB
from app.utils import generate_customer_id
from app.training import start_retrain
import json
import sys
from pathlib import Path
import csv
import io
from typing import List, Dict
import requests

from config import K_RETRAIN, MODEL_PATH
 

# Dynamically add the pipeline directory to Python path
# For Docker: use the copied pipeline in app/pipeline
# For local: use ml_pipeline/src/pipeline
BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_PIPELINE_DIR = Path(__file__).resolve().parent / "pipeline"
ML_PIPELINE_SRC = BASE_DIR / "ml_pipeline" / "src" / "pipeline"

# Add app/pipeline first (for Docker), then ml_pipeline/src/pipeline (for local)
if APP_PIPELINE_DIR.exists() and str(APP_PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(APP_PIPELINE_DIR))
    print(f"Added {APP_PIPELINE_DIR} to sys.path")

if ML_PIPELINE_SRC.exists() and str(ML_PIPELINE_SRC) not in sys.path:
    sys.path.insert(0, str(ML_PIPELINE_SRC))
    print(f"Added {ML_PIPELINE_SRC} to sys.path")

# FastAPI app initialization
app = FastAPI(title="Telco Churn Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

# > Model Endpoints
@app.post("/predictpyload", response_model=PredictResponse)
def predict_payload(payload: PredictRequest):
    """Endpoint to predict customer churn probability."""
    proba = predict_churn(payload.dict())
    return {"churn_probability": proba}

@app.post("/predict", response_model=PredictResponse)
def predict(payload: "PredictInput"):
    """
    TODO: make sure to handle two modes: best approach to separate them?
    Mode A: payload = {customer_id} -> fetch features depuis new_customers
    Mode B: payload = features complètes (incluant customer_id)
    """
    token = uuid4()

    data = payload.model_dump(exclude_none=True)

    # Mode ID only : payload contient uniquement customer_id
    if set(data.keys()) == {"customer_id"}:
        customer_id = data["customer_id"]

        conn = get_db_connection()
        try:
            features = fetch_customer_features(conn, customer_id)
        finally:
            conn.close()

        if features is None:
            raise HTTPException(status_code=404, detail="customer_id not found in customers") #TODO new_customers or customers??

    else:
        # Mode features : on s'attend à customer_id + toutes les features nécessaires
        features = data
        customer_id = features.get("customer_id")
        if not customer_id:
            raise HTTPException(status_code=400, detail="customer_id is required in features mode")

    
    # prédiction
    # model_features = get_model_info()["feature_names"]
    # features = {k: features[k] for k in model_features if k in features}
    print(features)
    proba = predict_churn(features)
    pred = 1 if proba >= 0.5 else 0 # TODO threshold configurable?

    # insert predictions (BIGSERIAL prediction_id) + token
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO predictions (customer_id, churn_score, churn_label, features_json, model_version, token)
                VALUES (%s, %s, %s, %s::jsonb, %s, %s)
                RETURNING prediction_id
                """,
                (customer_id, float(proba), bool(pred), json.dumps(features), "v1", str(token))
            )
            prediction_id = cur.fetchone()[0]
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"DB insert failed: {e}")
    finally:
        if conn:
            conn.close()

    return {
        "prediction_id": prediction_id,
        "token": token,
        "customer_id": customer_id,
        "churn_probability": float(proba),
        "prediction": pred
    }

@app.post("/predict/batch")
def predict_batch(payload: dict):
    """
    Predict churn for multiple customers.
    Expects: { "customer_ids": [id1, id2, ...] }
    Returns: { "message": "...", "predictions": [...], "failed": [...] }
    """
    customer_ids = payload.get("customer_ids", [])
    if not customer_ids:
        raise HTTPException(status_code=400, detail="customer_ids is required")
    
    predictions = []
    failed = []
    
    for customer_id in customer_ids:
        try:
            # Fetch customer features
            conn = get_db_connection()
            try:
                features = fetch_customer_features(conn, str(customer_id))
            finally:
                conn.close()
            
            if features is None:
                failed.append({"customer_id": customer_id, "error": "Customer not found"})
                continue
            
            # Make prediction
            proba = predict_churn(features)
            pred = 1 if proba >= 0.5 else 0
            
            # Insert into predictions table
            conn = get_db_connection()
            token = uuid4()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO predictions (customer_id, churn_score, churn_label, model_version, features_json, token)
                        VALUES (%s, %s, %s, %s, %s::jsonb, %s)
                        RETURNING prediction_id
                        """,
                        (
                            str(customer_id), 
                            float(proba), 
                            bool(pred), 
                            'v1', # MODEL_PATH.split("/")[-1],
                            json.dumps(features),
                            str(token)
                         )
                    )
                    prediction_id = cur.fetchone()[0]
                conn.commit()
                
                predictions.append({
                    "customer_id": customer_id,
                    "prediction_id": prediction_id,
                    "churn_probability": float(proba),
                    "churn_label": bool(pred)
                })
            except Exception as e:
                conn.rollback()
                failed.append({"customer_id": customer_id, "error": str(e)})
            finally:
                conn.close()
                
        except Exception as e:
            failed.append({"customer_id": customer_id, "error": str(e)})
    
    return {
        "message": f"Processed {len(predictions)} predictions, {len(failed)} failed",
        "predictions": predictions,
        "failed": failed
    }

@app.post("/predict/customer/{customer_id}")
def predict_customer(customer_id: str):
    """
    Predict churn for a single customer by ID.
    Returns: { "customer_id": "...", "prediction_id": ..., "churn_probability": ..., "churn_label": ... }
    """
    try:
        # Fetch customer features
        conn = get_db_connection()
        try:
            features = fetch_customer_features(conn, customer_id)
        finally:
            conn.close()
        
        if features is None:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Make prediction
        proba = predict_churn(features)
        pred = 1 if proba >= 0.5 else 0
        
        # Insert into predictions table
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO predictions (customer_id, churn_score, churn_label, model_version)
                    VALUES (%s, %s, %s, %s)
                    RETURNING prediction_id
                    """,
                    (customer_id, float(proba), bool(pred), "v1")
                )
                prediction_id = cur.fetchone()[0]
            conn.commit()
            
            return {
                "message": "Prediction completed successfully",
                "customer_id": customer_id,
                "prediction_id": prediction_id,
                "churn_probability": float(proba),
                "churn_label": bool(pred)
            }
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to save prediction: {e}")
        finally:
            conn.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model_info")
def model_info():
    """Return metadata about the loaded model to help integration."""
    return get_model_info()

# > Customer Data Endpoints
REQUIRED_UPLOAD_COLUMNS: List[str] = []

@app.get("/customers")
def get_customers():
    """Endpoint to fetch customer data."""
    try:
        customers = fetch_customers()
        return {"customers": customers}
    except Exception as e:
        return {"error": str(e)}

@app.get("/customers/{customer_id}")
def get_customer_by_id(customer_id: str):
    """Endpoint to fetch a customer by their ID."""
    try:
        customer = fetch_customer_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return {"customer": customer}
    except Exception as e:
        return {"error": str(e)}

@app.post("/customers/upload_csv")
async def upload_customers_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file containing customer records to insert/update into the `customers` table.

    Expected headers:
    customer_id,email,gender,senior_citizen,partner,dependents,tenure,phone_service,multiple_lines,
    internet_service,online_security,online_backup,device_protection,tech_support,streaming_tv,streaming_movies,
    contract,paperless_billing,payment_method,monthly_charges,total_charges

    Returns summary with processed rows and any per-row errors.
    """
    filename = file.filename or ""
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file")

    # Read and decode the uploaded CSV
    content_bytes = await file.read()
    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        # Fallback for BOM or other encodings
        content = content_bytes.decode("utf-8", errors="ignore")

    reader = csv.DictReader(io.StringIO(content))
    headers = [h.strip() for h in reader.fieldnames or []]
    missing = [c for c in REQUIRED_UPLOAD_COLUMNS if c not in headers]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {', '.join(missing)}"
        )

    conn = None
    processed = 0
    errors: List[Dict] = []
    try:
        conn = get_db_connection()
        conn.autocommit = False

        ensure_customers_table(conn)

        with conn.cursor() as cur:
            upsert_sql = (
                """
                INSERT INTO customers (
                    customer_id, gender, senior_citizen, partner, dependents, tenure,
                    phone_service, multiple_lines, internet_service, online_security, online_backup,
                    device_protection, tech_support, streaming_tv, streaming_movies, contract,
                    paperless_billing, payment_method, monthly_charges, total_charges,
                    churn, status, notified, first_name, last_name, email
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (customer_id) DO UPDATE SET
                    gender=EXCLUDED.gender,
                    senior_citizen=EXCLUDED.senior_citizen,
                    partner=EXCLUDED.partner,
                    dependents=EXCLUDED.dependents,
                    tenure=EXCLUDED.tenure,
                    phone_service=EXCLUDED.phone_service,
                    multiple_lines=EXCLUDED.multiple_lines,
                    internet_service=EXCLUDED.internet_service,
                    online_security=EXCLUDED.online_security,
                    online_backup=EXCLUDED.online_backup,
                    device_protection=EXCLUDED.device_protection,
                    tech_support=EXCLUDED.tech_support,
                    streaming_tv=EXCLUDED.streaming_tv,
                    streaming_movies=EXCLUDED.streaming_movies,
                    contract=EXCLUDED.contract,
                    paperless_billing=EXCLUDED.paperless_billing,
                    payment_method=EXCLUDED.payment_method,
                    monthly_charges=EXCLUDED.monthly_charges,
                    total_charges=EXCLUDED.total_charges,
                    churn=EXCLUDED.churn,
                    status=EXCLUDED.status,
                    notified=EXCLUDED.notified,
                    first_name=EXCLUDED.first_name,
                    last_name=EXCLUDED.last_name,
                    email=EXCLUDED.email,
                    updated_at=NOW()
                """
            )
            insert_no_conflict_sql = (
                """
                INSERT INTO customers (
                    customer_id, gender, senior_citizen, partner, dependents, tenure,
                    phone_service, multiple_lines, internet_service, online_security, online_backup,
                    device_protection, tech_support, streaming_tv, streaming_movies, contract,
                    paperless_billing, payment_method, monthly_charges, total_charges,
                    churn, status, notified, first_name, last_name, email
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (customer_id) DO NOTHING
                """
            )

            generated_ids: List[Dict] = []
            for row_idx, row in enumerate(reader, start=2):
                try:
                    # Validate and normalize via schema
                    cust = CustomerDB(**row)
                    # If customer_id is missing, generate and insert with conflict avoidance
                    if not cust.customer_id:
                        assigned_id = None
                        # Try a few times in the rare case of collision
                        for _ in range(8):
                            candidate = generate_customer_id()
                            values = (
                                candidate,
                                cust.gender,
                                cust.senior_citizen,
                                cust.partner,
                                cust.dependents,
                                cust.tenure,
                                cust.phone_service,
                                cust.multiple_lines,
                                cust.internet_service,
                                cust.online_security,
                                cust.online_backup,
                                cust.device_protection,
                                cust.tech_support,
                                cust.streaming_tv,
                                cust.streaming_movies,
                                cust.contract,
                                cust.paperless_billing,
                                cust.payment_method,
                                cust.monthly_charges,
                                cust.total_charges,
                                cust.churn,
                                cust.status,
                                cust.notified,
                                cust.first_name,
                                cust.last_name,
                                cust.email,
                            )
                            cur.execute(insert_no_conflict_sql, values)
                            if cur.rowcount == 1:
                                assigned_id = candidate
                                generated_ids.append({"row": row_idx, "customer_id": assigned_id})
                                processed += 1
                                break
                        if not assigned_id:
                            raise ValueError("Failed to assign unique customer_id after multiple attempts")
                    else:
                        # Explicit ID present -> upsert
                        values = (
                            cust.customer_id,
                            cust.gender,
                            cust.senior_citizen,
                            cust.partner,
                            cust.dependents,
                            cust.tenure,
                            cust.phone_service,
                            cust.multiple_lines,
                            cust.internet_service,
                            cust.online_security,
                            cust.online_backup,
                            cust.device_protection,
                            cust.tech_support,
                            cust.streaming_tv,
                            cust.streaming_movies,
                            cust.contract,
                            cust.paperless_billing,
                            cust.payment_method,
                            cust.monthly_charges,
                            cust.total_charges,
                            cust.churn,
                            cust.status,
                            cust.notified,
                            cust.first_name,
                            cust.last_name,
                            cust.email,
                        )
                        cur.execute(upsert_sql, values)
                        processed += 1
                except Exception as e:
                    errors.append({"row": row_idx, "error": str(e)})

        conn.commit()

        return {
            "status": "ok",
            "processed": processed,
            "errors": errors,
            "required_columns": REQUIRED_UPLOAD_COLUMNS,
            "target_table": "customers",
            "generated_ids": generated_ids,
        }

    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

# > Feedback and Retraining Endpoints

@app.post("/feedback", response_model=FeedbackResponse)
def feedback(payload: FeedbackRequest, background: BackgroundTasks):
    """
    Reçoit token + answer YES/NO + feedback_label 0/1
    -> retrouve prediction_id via token (predictions)
    -> insert feedback
    -> count feedback non utilisés (used_for_training=false)
    -> trigger retrain si >= K_RETRAIN (tu brancheras /retrain après)
    """
    conn = None
    try:
        conn = get_db_connection()
        conn.autocommit = False

        with conn.cursor() as cur:
            # 1) retrouver prediction_id via token
            cur.execute("SELECT prediction_id FROM predictions WHERE token=%s", (str(payload.token),))
            row = cur.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="token not found")
            prediction_id = row[0]

            # 2) insérer feedback (1 feedback max par prediction_id)
            try:
                cur.execute(
                    """
                    INSERT INTO feedback (prediction_id, answer, feedback_label, used_for_training, sent_at, answered_at)
                    VALUES (%s, %s, %s, FALSE, NOW(), NOW())
                    """,
                    (prediction_id, payload.answer, int(payload.feedback_label))
                )
            except UniqueViolation:
                raise HTTPException(status_code=409, detail="feedback already received for this prediction_id")

            # 3) compter les feedbacks non utilisés
            cur.execute("SELECT COUNT(*) FROM feedback WHERE used_for_training = FALSE")
            new_feedback_count = int(cur.fetchone()[0])

            retrain_triggered = (new_feedback_count >= K_RETRAIN)

        conn.commit()
        # Déclencher /retrain via la logique training_runs
        if retrain_triggered:
            background.add_task(start_retrain, "feedback") 


        return {
            "status": "ok",
            "feedback_count": new_feedback_count,
            "retrain_triggered": retrain_triggered
        }

    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@app.post("/retrain")
def retrain(payload: RetrainRequest):
    return start_retrain(payload.reason)

@app.post("/notify")
def notify_customers(payload: dict):
    """
    Notify customers who have predictions via n8n webhook.
    Expects: { "customer_ids": [id1, id2, ...] }
    Returns: { "message": "...", "notified": [...], "failed": [...] }
    """
    customer_ids = payload.get("customer_ids", [])
    if not customer_ids:
        raise HTTPException(status_code=400, detail="customer_ids is required")
    
    notified = []
    failed = []
    
    for customer_id in customer_ids:
        try:
            # Check if customer has a prediction
            conn = get_db_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT prediction_id, churn_score, churn_label, token
                        FROM predictions 
                        WHERE customer_id = %s 
                        ORDER BY created_at DESC 
                        LIMIT 1
                        """,
                        (str(customer_id),)
                    )
                    prediction_row = cur.fetchone()
                    
                    if not prediction_row:
                        failed.append({"customer_id": customer_id, "error": "No prediction found"})
                        continue
                    
                    prediction_id = prediction_row[0]
                    token = prediction_row[3]
            finally:
                conn.close()
            
            # Call n8n webhook to send notification
            webhook_url = "http://n8n:5678/webhook/notify-churn"
            webhook_payload = {"customer_id": str(customer_id), 
                               'token': str(token),}
            
            try:
                response = requests.post(
                    webhook_url,
                    json=webhook_payload,
                    timeout=10
                )
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                failed.append({"customer_id": customer_id, "error": f"Webhook failed: {str(e)}"})
                continue
            
            # Insert/update feedback table with sent_at timestamp
            conn = get_db_connection()
            try:
                with conn.cursor() as cur:
                    # Check if feedback already exists for this prediction
                    cur.execute(
                        "SELECT feedback_id FROM feedback WHERE prediction_id = %s",
                        (prediction_id,)
                    )
                    existing = cur.fetchone()
                    
                    if existing:
                        # Update sent_at timestamp
                        cur.execute(
                            "UPDATE feedback SET sent_at = NOW() WHERE prediction_id = %s",
                            (prediction_id,)
                        )
                    else:
                        # Insert new feedback record
                        cur.execute(
                            """
                            INSERT INTO feedback (prediction_id, sent_at, used_for_training)
                            VALUES (%s, NOW(), FALSE)
                            """,
                            (prediction_id,)
                        )
                conn.commit()
                
                notified.append({
                    "customer_id": customer_id,
                    "prediction_id": prediction_id,
                    "status": "notified"
                })
            except Exception as e:
                conn.rollback()
                failed.append({"customer_id": customer_id, "error": f"Failed to update feedback: {str(e)}"})
            finally:
                conn.close()
                
        except Exception as e:
            failed.append({"customer_id": customer_id, "error": str(e)})
    
    return {
        "message": f"Notified {len(notified)} customers, {len(failed)} failed",
        "notified": notified,
        "failed": failed
    }

