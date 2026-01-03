from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import PredictInput, PredictRequest, PredictResponse
from app.predict import predict_churn
from app.model import get_model_info
from app.data_fetch import fetch_customers, fetch_customer_by_id, fetch_customer_features
from uuid import uuid4
from app.db_connection import get_db_connection
from psycopg2.errors import UniqueViolation
from app.schemas import FeedbackRequest, FeedbackResponse, RetrainRequest
import json
import sys
from pathlib import Path

# Dynamically add the ml_pipeline/src/pipeline/ directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ML_PIPELINE_SRC = BASE_DIR / "ml_pipeline" / "src" / "pipeline"
if ML_PIPELINE_SRC not in sys.path:
    sys.path.append(str(ML_PIPELINE_SRC))


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

@app.get("/model_info")
def model_info():
    """Return metadata about the loaded model to help integration."""
    return get_model_info()


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


K_RETRAIN = 20  # exemple

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
            background.add_task(_trigger_retrain_internal) 


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

def _trigger_retrain_internal():
    # On réutilise la logique /retrain existante (training_runs + cooldown + lock)
    retrain(RetrainRequest(reason="feedback"))


COOLDOWN_MINUTES = 10  # anti-boucle

@app.post("/retrain")
def retrain(payload: RetrainRequest):
    conn = None
    try:
        conn = get_db_connection()
        conn.autocommit = False

        with conn.cursor() as cur:
            # 1) cooldown: si retrain récent, skip
            cur.execute("""
                SELECT started_at
                FROM training_runs
                WHERE status IN ('started','success')
                ORDER BY started_at DESC
                LIMIT 1
            """)
            last = cur.fetchone()
            if last is not None:
                # côté DB on fait simple: si < cooldown minutes, on refuse
                cur.execute("SELECT NOW() - %s::timestamptz < (%s || ' minutes')::interval",
                            (last[0], COOLDOWN_MINUTES))
                too_soon = cur.fetchone()[0]
                if too_soon:
                    conn.commit()
                    return {"status": "skipped", "message": "cooldown active"}

            # 2) lock “soft” : si un run started existe, refuse
            cur.execute("SELECT COUNT(*) FROM training_runs WHERE status='started'")
            if cur.fetchone()[0] > 0:
                conn.commit()
                return {"status": "skipped", "message": "retrain already running"}

            # 3) create run
            cur.execute("""
                INSERT INTO training_runs (reason, status)
                VALUES (%s, 'started')
                RETURNING run_id
            """, (payload.reason,))
            run_id = cur.fetchone()[0]

            # 4) snapshot nouveaux feedback (pour reset compteur)
            cur.execute("SELECT COUNT(*) FROM feedback WHERE used_for_training=FALSE")
            new_feedback = int(cur.fetchone()[0])

            # 5) reset compteur (on marque comme utilisés) — prend tout le backlog
            cur.execute("""
                UPDATE feedback
                SET used_for_training = TRUE
                WHERE used_for_training = FALSE
            """)

        conn.commit()

        # 6) retrain réel (à brancher)
        retrain_and_reload_model(reason=payload.reason)

        # 7) success
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE training_runs
                SET status='success', ended_at=NOW(), notes=%s
                WHERE run_id=%s
            """, (f"used_new_feedback={new_feedback}", run_id))
        conn.commit()

        return {"status": "ok", "run_id": run_id, "reason": payload.reason, "used_new_feedback": new_feedback}

    except Exception as e:
        # mark failed si possible
        try:
            if conn:
                conn.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()


def retrain_and_reload_model(reason: str):
    """
    Branche ici votre vrai retrain.
    - tu peux réentraîner sur ref + TOUT feedback (même anciens)
    - le reset used_for_training sert juste à gérer le déclenchement
    """
    print(f"Retraining... reason={reason} (placeholder)")