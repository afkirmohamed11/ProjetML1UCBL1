# n8n – Setup local avec Docker

Ce projet utilise **n8n en local via Docker**.
Les workflows et credentials sont persistés grâce à un volume Docker.

---

## 1) Lancer n8n

Depuis la racine du projet :

```bash
docker compose up -d n8n
```

Accéder à n8n :
[http://localhost:5678](http://localhost:5678)

---

## 2) Persistance des données n8n

n8n sauvegarde automatiquement :

* le compte utilisateur
* les workflows importés
* les credentials

dans un **volume Docker** :

```yml
n8n_data:/home/node/.n8n
```

➡️ Tant que le volume existe, les données sont conservées.

---

## 3) Variables d’environnement

Créer le fichier `.env` à la racine :

```bash
cp .env.n8n.example .env
```

Exemple `.env` :

```env
# n8n
N8N_ENCRYPTION_KEY=change_me
TZ=Europe/Paris

# OpenAI
OPENAI_API_KEY=sk-xxxxxxxx

# SMTP
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=587
SMTP_USER=xxxx
SMTP_PASS=yyyy

# Postgres
POSTGRES_HOST=xxxx
POSTGRES_PORT=5432
POSTGRES_DB=xxxx
POSTGRES_USER=xxxx
POSTGRES_PASSWORD=xxxx
```

Après modification :

```bash
docker compose restart n8n
```

---

## 4) Importer les workflows (une seule fois)

Dans l’interface n8n :

1. **Workflows**
2. **Import from file**
3. Importer les fichiers `.json`

Les workflows sont ensuite sauvegardés dans la base n8n.

---

## 5) Créer les credentials n8n (une seule fois)

### a) Postgres

Type : **Postgres**

Champs (en expression) :

```text
Host: {{$env.POSTGRES_HOST}}
Port: {{$env.POSTGRES_PORT}}
Database: {{$env.POSTGRES_DB}}
User: {{$env.POSTGRES_USER}}
Password: {{$env.POSTGRES_PASSWORD}}
```

**Important**

* Activer : **Ignore SSL issues**
* Nécessaire pour éviter les erreurs SSL en local

---

### b) OpenAI

Type : **OpenAI**

```text
API Key: {{$env.OPENAI_API_KEY}}
```

---

### c) SMTP (Mail)

Type : **SMTP**

```text
Host: {{$env.SMTP_HOST}}
Port: {{$env.SMTP_PORT}}
User: {{$env.SMTP_USER}}
Password: {{$env.SMTP_PASS}}
```

Configuration :

* SSL/TLS  **désactivé**
* Disable STARTTLS  **désactivé**

---

## 6) Exemple – Déclencher le webhook `notify-churn`

### 1) Payload JSON attendu

```json
{
  "token" = "7b9d6c7e-1d0c-4c2e-9f1c-2a4e3a9e8f11"
  "customer_id" = "7590-VHVEG"
}

```

> `prediction`: 1 = churn, 0 = non churn (à adapter selon ton workflow).

### 2) Test en PowerShell (Windows)

```powershell
$body = @{
  token = "7b9d6c7e-1d0c-4c2e-9f1c-2a4e3a9e8f11"
  customer_id = "7590-VHVEG"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:5678/webhook-test/notify-churn" `
  -ContentType "application/json" `
  -Body $body
```

### 3) Test en curl (Linux / macOS / Git Bash)

```bash
curl -X POST "http://localhost:5678/webhook-test/notify-churn" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "7b9d6c7e-1d0c-4c2e-9f1c-2a4e3a9e8f11",
    "customer_id": "7590-VHVEG",
  }'
```
## Nettoyage – Supprimer un feedback de test (PostgreSQL)

Si tu relances plusieurs fois le **même test** (même `prediction_id`), tu risques de te heurter à un doublon (selon les contraintes de ta table).  
Tu peux supprimer l’entrée de test déjà enregistrée avec la requête suivante :

```sql
DELETE FROM public.feedback
WHERE prediction_id = 2;
```
---

## 7) À propos des warnings “env access denied”

Il est **normal** de voir des champs en rouge avec :

> *No access to environment variable*

➡️ C’est **un problème d’interface uniquement**
➡️ **L’exécution fonctionne correctement**
➡️ Tant que le workflow s’exécute sans erreur, c’est OK

---

## 8) Redémarrer / arrêter n8n

```bash
docker compose stop n8n
docker compose start n8n
```

---

## 9) Reset complet n8n (supprime tout)

Supprime workflows + credentials + compte :

```bash
docker compose down -v
docker compose up -d n8n
```

---

