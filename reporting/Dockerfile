FROM python:3.11-slim

WORKDIR /app

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tous les fichiers nécessaires
COPY . .

# Exposer le port pour Prometheus
EXPOSE 8020

# Lancer le service d'export des métriques
CMD ["python", "metrics_exporter.py"]