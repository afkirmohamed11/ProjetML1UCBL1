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

3. **Upload Customers CSV**
    - **POST** `/customers/upload_csv`
    - Content-Type: `multipart/form-data`
    - Form field: `file` (CSV)
    - Inserts/updates records into `customers` table.
    - Required header: `customer_id`. All other headers are optional and validated/coerced via schema.
    - Common headers:
       `customer_id,gender,senior_citizen,partner,dependents,tenure,phone_service,multiple_lines,internet_service,online_security,online_backup,device_protection,tech_support,streaming_tv,streaming_movies,contract,paperless_billing,payment_method,monthly_charges,total_charges,churn,status,notified_date,first_name,last_name,email`
    - Example:
       ```bash
       curl -X POST \
          -F "file=@backend/app/artifacts/sample_new_customers.csv" \
          http://localhost:8080/customers/upload_csv
       ```

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