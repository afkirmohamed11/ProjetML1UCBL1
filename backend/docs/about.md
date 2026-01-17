# Telco Churn Prediction System

## Overview
This system predicts customer churn for a telecommunications company using machine learning.

## Features
- **Churn Prediction**: Predict whether a customer will churn based on their profile
- **Customer Management**: View and manage customer information
- **Model Retraining**: Retrain the model with new feedback data
- **Chatbot**: Ask questions about the system or query data using natural language

## How it works
1. Customer data is collected including tenure, services, and billing information
2. The ML model analyzes patterns to predict churn probability
3. Predictions are stored and can be reviewed
4. User feedback improves the model over time

## Key Factors for Churn
- **Contract type**: Month-to-month contracts have higher churn rates
- **Tenure**: Newer customers are more likely to churn
- **Monthly charges**: Higher charges correlate with increased churn
- **Internet service type**: Fiber optic users show different patterns
- **Payment method**: Electronic check users tend to churn more


## Model Information
The prediction model uses various customer features:
- Demographics: senior_citizen, partner, dependents
- Services: internet_service, online_security, tech_support
- Account: contract, paperless_billing, payment_method
- Billing: monthly_charges, total_charges
