-- Table schema for the Telco Customer Churn dataset

CREATE DATABASE telco_churn;
CREATE SCHEMA public;
CREATE TABLE public.customers (
    customer_id        TEXT PRIMARY KEY,
    gender             TEXT,
    senior_citizen     BOOLEAN,
    partner            BOOLEAN,
    dependents         BOOLEAN,
    tenure             INTEGER,

    phone_service      BOOLEAN,
    multiple_lines     TEXT,

    internet_service   TEXT,
    online_security    TEXT,
    online_backup      TEXT,
    device_protection  TEXT,
    tech_support       TEXT,
    streaming_tv       TEXT,
    streaming_movies   TEXT,

    contract            TEXT,
    paperless_billing   BOOLEAN,
    payment_method      TEXT,

    monthly_charges     NUMERIC(10,2),
    total_charges       NUMERIC(10,2),

    churn               BOOLEAN
);


-- TO insert the cvs in the database, use the following command in psql (PSQL TOOL):
\copy public.customers FROM 'C:\Users\Dell\Downloads\ref_data.csv' DELIMITER ',' CSV HEADER NULL ' '; 
