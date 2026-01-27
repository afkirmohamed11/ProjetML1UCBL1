# Data Preprocessing Documentation

This document outlines the data preprocessing steps applied to the customer churn dataset. The goal is to transform the raw data (`customers_data.csv`) into a format suitable for machine learning prediction, resulting in `preprocessed_data.csv`.

## Overview of Preprocessing

The `preprocess_data` function orchestrates several cleaning and transformation steps:

1.  **Duplicate Removal**: Ensures each customer entry is unique.
2.  **Missing Value Imputation**: Handles missing values in key numeric columns.
3.  **Boolean Feature Encoding**: Converts 'Yes'/'No' or equivalent boolean columns to numerical (0/1).
4.  **Customer ID Removal**: Drops identifier columns not relevant for modeling.
5.  **Service Feature Encoding**: Transforms specific service-related categorical features into binary integers.
6.  **Categorical Feature One-Hot Encoding**: Converts multi-category nominal features into a numerical representation using one-hot encoding.
7.  **Redundant Column Removal**: Drops columns identified as redundant or highly correlated with others.
8.  **Numeric Feature Scaling**: Standardizes numerical features to a common scale.
9.  **Low-Impact Feature Removal**: Discards features found to have minimal predictive value based on prior analysis.

## Column Changes Summary

### Original Columns in `customers_data.csv` (Example)

*   `customer_id`
*   `gender`
*   `senior_citizen`
*   `partner`
*   `dependents`
*   `tenure`
*   `phone_service`
*   `multiple_lines`
*   `internet_service`
*   `online_security`
*   `online_backup`
*   `device_protection`
*   `tech_support`
*   `streaming_tv`
*   `streaming_movies`
*   `contract`
*   `paperless_billing`
*   `payment_method`
*   `monthly_charges`
*   `total_charges`
*   `churn`

### Columns Added

The following columns are *added* as a result of one-hot encoding categorical features:

*   `gender_Male`
*   `internet_service_DSL`
*   `internet_service_Fiber_optic`
*   `contract_One_year`
*   `contract_Two_year`
*   `payment_method_Electronic_check`
*   `payment_method_Mailed_check`
*   `payment_method_Bank_transfer`

### Columns Removed

Various columns are *removed* throughout the preprocessing pipeline:

*   **`customer_id`**: Removed by `drop_customer_id`.
*   **Original Categorical Columns**: `gender`, `internet_service`, `contract`, `payment_method` are removed by `encode_categorical_features` after their one-hot encoded versions are created.
*   **Redundant Columns**: `tenure`, `gender_Female`, `contract_Month_to_month`, `payment_method_Credit_card` are removed by `drop_redundant_columns`.
*   **Low Impact Features**: `gender_Male`, `phone_service`, `multiple_lines`, `streaming_tv`, `streaming_movies`, `online_backup`, `device_protection` are removed by `drop_low_impact_features`.

## Function-wise Column Usage

Here's a breakdown of which preprocessing function affects which columns:

*   **`drop_duplicates(df)`**:
    *   **Action**: Removes duplicate rows.
    *   **Columns Affected**: All (row-wise operation).

*   **`fill_total_charges_median(df)`**:
    *   **Action**: Fills null values with the median.
    *   **Columns Affected**: `total_charges`.

*   **`encode_boolean_features(df)`**:
    *   **Action**: Converts boolean-like values to 0/1 integers.
    *   **Columns Affected**: `senior_citizen`, `partner`, `dependents`, `phone_service`, `paperless_billing`, `churn`.

*   **`drop_customer_id(df)`**:
    *   **Action**: Removes the customer identifier column.
    *   **Columns Affected**: `customer_id`.

*   **`encode_service_features(df)`**:
    *   **Action**: Converts service-related 'Yes'/'No' categories to 0/1 integers.
    *   **Columns Affected**: `multiple_lines`, `online_security`, `online_backup`, `device_protection`, `tech_support`, `streaming_tv`, `streaming_movies`.

*   **`encode_categorical_features(df)`**:
    *   **Action**: Creates new one-hot encoded columns and drops original categorical columns.
    *   **Columns Affected (Original Dropped)**: `gender`, `internet_service`, `contract`, `payment_method`.
    *   **Columns Affected (New Added)**: `gender_Male`, `gender_Female`, `internet_service_DSL`, `internet_service_Fiber_optic`, `contract_Month_to_month`, `contract_One_year`, `contract_Two_year`, `payment_method_Electronic_check`, `payment_method_Mailed_check`, `payment_method_Bank_transfer`, `payment_method_Credit_card`.

*   **`drop_redundant_columns(df)`**:
    *   **Action**: Removes columns identified as redundant.
    *   **Columns Affected**: `tenure`, `gender_Female`, `contract_Month_to_month`, `payment_method_Credit_card`.

*   **`scale_numeric_features(df)`**:
    *   **Action**: Scales numeric features using `StandardScaler`.
    *   **Columns Affected**: `monthly_charges`, `total_charges`.

*   **`drop_low_impact_features(df)`**:
    *   **Action**: Removes features with low predictive impact.
    *   **Columns Affected**: `gender_Male`, `phone_service`, `multiple_lines`, `streaming_tv`, `streaming_movies`, `online_backup`, `device_protection`.

## Final Data Structure for Prediction

After all preprocessing steps, the resulting DataFrame will contain the transformed features suitable for a machine learning model. Frontend input should correspond to these final feature columns, and it's crucial to apply the same preprocessing logic to any new data before making predictions.

### Remaining Columns (After Preprocessing)

| Column                       | Ancestor / Original Column(s)                  |
|-------------------------------|-----------------------------------------------|
| senior_citizen               | senior_citizen                                |
| partner                       | partner                                       |
| dependents                    | dependents                                    |
| online_security               | online_security                               |
| tech_support                  | tech_support                                  |
| paperless_billing             | paperless_billing                             |
| monthly_charges               | monthly_charges                               |
| total_charges                 | total_charges                                 |
| churn                         | churn                                         |
| internet_service_DSL          | internet_service                              |
| internet_service_Fiber_optic  | internet_service                              |
| contract_One_year             | contract                                      |
| contract_Two_year             | contract                                      |
| payment_method_Electronic_check | payment_method                               |
| payment_method_Mailed_check    | payment_method                               |
| payment_method_Bank_transfer   | payment_method                               |