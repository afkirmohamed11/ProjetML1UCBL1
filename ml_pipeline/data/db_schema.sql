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

    churn               BOOLEAN,
    status              VARCHAR(20),
    notified_date       BOOLEAN,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    
    first_name          VARCHAR(50),
    last_name           VARCHAR(50),
    email               VARCHAR(100)
);

-- This wouldn't work because we added other columns on the reference csv file !!!
-- TO insert the cvs in the database, use the following command in psql (PSQL TOOL):
\copy public.customers FROM 'C:\Users\Dell\Downloads\ref_data.csv' DELIMITER ',' CSV HEADER NULL ' '; 


-- trained_models

CREATE TABLE IF NOT EXISTS trained_models (
  model_version     TEXT PRIMARY KEY,                         -- e.g. 'v1', 'v1.1'
  training_reason   TEXT NOT NULL,                            -- e.g. threshold, data refresh, performance degradation
  status            TEXT NOT NULL DEFAULT 'running',           -- running | success | failed
  started_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  ended_at          TIMESTAMPTZ,
  notes             TEXT,

  CONSTRAINT trained_models_status_chk
    CHECK (status IN ('running', 'success', 'failed')),

  CONSTRAINT trained_models_end_after_start_chk
    CHECK (ended_at IS NULL OR ended_at >= started_at)
);

-- 2) predictions

CREATE TABLE IF NOT EXISTS predictions (
  prediction_id   BIGSERIAL PRIMARY KEY,
  customer_id     TEXT NOT NULL,                               -- FK -> customers.customer_id (type must match your customers table)
  churn_score     DOUBLE PRECISION NOT NULL,
  churn_label     BOOLEAN NOT NULL,                             -- true/false
  features_json   JSONB NOT NULL DEFAULT '{}'::jsonb,
  model_version   TEXT NOT NULL,                                -- EXACT SAME value as trained_models.model_version
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT predictions_churn_score_chk
    CHECK (churn_score >= 0 AND churn_score <= 1)
);

-- FK: predictions -> customers
ALTER TABLE predictions
  ADD CONSTRAINT predictions_customer_fk
  FOREIGN KEY (customer_id)
  REFERENCES customers(customer_id)
  ON UPDATE CASCADE
  ON DELETE RESTRICT;


-- FK: predictions -> trained_models
ALTER TABLE predictions
  ADD CONSTRAINT predictions_model_version_fk
  FOREIGN KEY (model_version)
  REFERENCES trained_models(model_version)
  ON UPDATE CASCADE
  ON DELETE RESTRICT;
-- FK: customer -> prediction
ALTER TABLE predictions
  ADD CONSTRAINT predictions_customer_fk
  FOREIGN KEY (customer_id)
  REFERENCES public.customers(customer_id)
  ON UPDATE CASCADE
  ON DELETE CASCADE; 

-- 3) feedback

CREATE TABLE IF NOT EXISTS feedback (
  feedback_id     BIGSERIAL PRIMARY KEY,
  prediction_id   BIGINT NOT NULL,                              -- FK -> predictions.prediction_id
  answer          TEXT,                                         -- Text: 'Yes' / 'No' (as you described)
  feedback_label  BOOLEAN,                                      -- boolean label
  sent_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  answered_at     TIMESTAMPTZ,

);

ALTER TABLE feedback
  ADD CONSTRAINT feedback_prediction_fk
  FOREIGN KEY (prediction_id)
  REFERENCES predictions(prediction_id)
  ON UPDATE CASCADE
  ON DELETE CASCADE;

