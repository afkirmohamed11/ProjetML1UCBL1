# Extend the official Apache Airflow image
FROM apache/airflow:2.9.0

# Switch to root user to install system packages
USER root


# Switch back to the airflow user
USER "${AIRFLOW_UID:-50000}"

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt