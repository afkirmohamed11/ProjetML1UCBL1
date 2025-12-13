# Backend for Churn Prediction API

This backend is built using **FastAPI** to serve a machine learning model for predicting customer churn in the telecommunications industry.

## Features
- **Health Check Endpoint**: Verify the API is running.
- **Prediction Endpoint**: Submit customer data and receive churn probability.
- **TODO**: more features (auth, roles, mlops, endpoints...)

## Project Structure
```
backend/
├── app/
│   ├── main.py        # Entry point for the FastAPI application
│   ├── model.py       # Handles model loading, etc
│   ├── predict.py     # Contains prediction logic
│   ├── schemas.py     # Defines request and response schemas
│   └── artifacts/     # Directory for storing the machine learning model
├── config.py          # Configuration file (e.g., model path)
```

## Endpoints
1. **Health Check**
   - **GET** `/health`
   - Response: `{ "status": "ok" }`

2. **Prediction**
   - **POST** `/predict`
   - Request Body: Customer data in JSON format
   - Response: `{ "churn_probability": <float> }`

## Setup Instructions
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   uvicorn app.main:app --reload --port 8080
   ```

3. **Access API Documentation**:
   - Swagger UI: [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)

## Notes
- Run the app from inside **backend** folder
- Update the `MODEL_PATH` in `config.py` if the model file location changes.