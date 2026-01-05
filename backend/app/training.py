from fastapi import HTTPException
from app.db_connection import get_db_connection

COOLDOWN_MINUTES = 10  # anti-boucle


def retrain_and_reload_model(reason: str):
    """
    Branche ici votre vrai retrain.
    - tu peux réentraîner sur ref + TOUT feedback (même anciens)
    - le reset used_for_training sert juste à gérer le déclenchement
    """
    print(f"Retraining... reason={reason} (placeholder)")


def start_retrain(reason: str):
    conn = None
    try:
        conn = get_db_connection()
        conn.autocommit = False

        with conn.cursor() as cur:
            # 1) cooldown: si retrain récent, skip
            cur.execute(
                """
                SELECT started_at
                FROM training_runs
                WHERE status IN ('started','success')
                ORDER BY started_at DESC
                LIMIT 1
                """
            )
            last = cur.fetchone()
            if last is not None:
                cur.execute(
                    "SELECT NOW() - %s::timestamptz < (%s || ' minutes')::interval",
                    (last[0], COOLDOWN_MINUTES),
                )
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
            cur.execute(
                """
                INSERT INTO training_runs (reason, status)
                VALUES (%s, 'started')
                RETURNING run_id
                """,
                (reason,),
            )
            run_id = cur.fetchone()[0]

            # 4) snapshot nouveaux feedback (pour reset compteur)
            cur.execute("SELECT COUNT(*) FROM feedback WHERE used_for_training=FALSE")
            new_feedback = int(cur.fetchone()[0])

            # 5) reset compteur (on marque comme utilisés) — prend tout le backlog
            cur.execute(
                """
                UPDATE feedback
                SET used_for_training = TRUE
                WHERE used_for_training = FALSE
                """
            )

        conn.commit()

        # 6) retrain réel (à brancher)
        retrain_and_reload_model(reason=reason)

        # 7) success
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE training_runs
                SET status='success', ended_at=NOW(), notes=%s
                WHERE run_id=%s
                """,
                (f"used_new_feedback={new_feedback}", run_id),
            )
        conn.commit()

        return {
            "status": "ok",
            "run_id": run_id,
            "reason": reason,
            "used_new_feedback": new_feedback,
        }

    except Exception as e:
        try:
            if conn:
                conn.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()
