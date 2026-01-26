import os
import logging
import requests
from requests.auth import HTTPBasicAuth
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AirflowTrigger")

class AirflowClient:
    def __init__(self):
        # Use Docker service name 'airflow-webserver' as default for container-to-container comms
        self.host = os.getenv("AIRFLOW_HOST", "airflow-webserver")
        self.port = os.getenv("AIRFLOW_PORT", "8080")
        self.username = os.getenv("AIRFLOW_USER", "airflow")
        self.password = os.getenv("AIRFLOW_PASSWORD", "airflow")
        
        self.base_url = f"http://{self.host}:{self.port}/api/v1"
        self.auth = HTTPBasicAuth(self.username, self.password)

    def trigger_dag(self, dag_id: str, payload_conf: Optional[Dict[str, Any]] = None) -> bool:
        """
        Triggers an Airflow DAG via the REST API.
        """
        endpoint = f"{self.base_url}/dags/{dag_id}/dagRuns"
        payload = {"conf": payload_conf or {}}
        
        logger.info("Initiating trigger for DAG: %s", dag_id)

        try:
            response = requests.post(
                endpoint,
                json=payload,
                auth=self.auth,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                logger.info("DAG Run created successfully. Run ID: %s", data.get('dag_run_id'))
                return True
            
            self._handle_errors(response, dag_id)
            return False

        except requests.exceptions.RequestException as e:
            logger.error("Connection failed: %s", str(e))
            return False

    def _handle_errors(self, response: requests.Response, dag_id: str):
        status_map = {
            401: "Authentication failed: invalid credentials.",
            404: f"DAG '{dag_id}' not found. Ensure it is unpaused in the UI.",
            409: "Conflict: A DAG run is already in progress.",
        }
        error_msg = status_map.get(response.status_code, f"Unexpected error: {response.text}")
        logger.error("Error %d: %s", response.status_code, error_msg)


def send_trigger():
    client = AirflowClient()
    params = {
        "trigger_source": "evidently_exporter",
        "reason": "data_drift_detected"
    }
    client.trigger_dag("ml_retraining_pipeline", payload_conf=params)
    logging.info("Airflow trigger function executed.")