# Data Pipeline - Medallion Architecture

This folder contains the real-time data streaming pipeline that implements the medallion architecture (bronze → silver → gold) for processing customer data from Azure Event Hub through ADLS Gen2 to AWS database.

## Medallion Architecture Overview

The pipeline follows a three-layer medallion architecture:

- **Bronze Layer:** Raw streaming data from Azure Event Hub (Kafka) stored in container
- **Silver Layer:** Cleansed, deduplicated, and processed data stored in ADLS Gen2
- **Gold Layer:** Aggregated, business-ready data stored in AWS database for analytics and ML

## Components

The pipeline consists of two main components:

### Producer
- **Location:** `producer/`
- **Purpose:** Produces customer data to Azure Event Hub (Kafka)
- **Components:**
  - `streamer.py` - Main producer script that sends customer data
  - `utils.py` - Utility functions for data processing
  - `Dockerfile` - Container image for the producer service
  - `requirements.txt` - Python dependencies

### Consumer
- **Location:** `consumer/`
- **Purpose:** Consumes streaming data from Kafka, processes it, and manages the silver and gold layer transformations
- **Notebooks:**
  - `Spark Structured Streaming.ipynb` - Reads from Event Hub (bronze), processes data, and writes to ADLS Gen2 (silver layer)
  - `silver_to_postgres.ipynb` - Transforms silver layer data and loads into AWS database (gold layer)

## Data Flow

```
Producer (Event Hub)
    ↓
Kafka/Event Hub
    ↓
BRONZE LAYER (Raw Stream)
    ↓
Spark Structured Streaming Consumer
    ↓
SILVER LAYER (ADLS Gen2 - Cleaned, Deduplicated, Partitioned)
    ↓
Data Transformation & Aggregation
    ↓
GOLD LAYER (AWS Database - Business Ready)
    ↓
Analytics, ML Models, Reporting
```

## Setup Instructions

### Prerequisites
- Azure Event Hub namespace and instance
- Azure Data Lake Storage Gen2 account
- Azure Service Principal (for authentication)
- Spark cluster with Databricks or similar environment
- Python 3.7+

### Configuration

1. **Producer Configuration** (`producer/`)
   ```bash
   cd producer
   pip install -r requirements.txt
   # Update connection strings in streamer.py
   python streamer.py
   ```

2. **Consumer Configuration** (`consumer/Spark Structured Streaming.ipynb` - Bronze to Silver)
   - Update the following variables:
     - `eh_namespace` - Azure Event Hub namespace
     - `eh_name` - Event Hub name
     - `eh_connection_string` - Connection string from Event Hub
     - `storage_account` - ADLS Gen2 account name
     - `container` - ADLS Gen2 container name
     - `client_id`, `tenant_id`, `client_secret` - Service Principal credentials

3. **Gold Layer Configuration** (`consumer/silver_to_postgres.ipynb` - Silver to Gold)
   - AWS database connection details
   - ADLS Gen2 credentials for reading silver layer data

### Running the Pipeline

1. **Start the Producer:**
   ```bash
   cd producer
   python streamer.py
   ```

2. **Run the Consumer (Bronze to Silver):**
   - Open `consumer/Spark Structured Streaming.ipynb` in Databricks
   - Execute cells in sequence
   - The streaming job will run continuously, processing data every 1 minute
   - Processed data lands in ADLS Gen2 silver layer

3. **Load Gold Layer (Silver to AWS):**
   - Run `consumer/silver_to_postgres.ipynb` to transform and load data to AWS database
   - This job can be scheduled as a batch or incremental pipeline

## Data Schema

The pipeline processes customer data with the following schema:

| Field | Type | Description |
|-------|------|-------------|
| customer_id | String | Unique customer identifier |
| gender | String | Customer gender |
| senior_citizen | Boolean | Senior citizen status |
| partner | Boolean | Has partner |
| dependents | Boolean | Has dependents |
| tenure | Integer | Months as customer |
| phone_service | Boolean | Has phone service |
| internet_service | String | Internet service type |
| contract | String | Contract type |
| monthly_charges | Decimal | Monthly charge amount |
| total_charges | Decimal | Total charges (calculated if missing) |
| updated_at | Timestamp | Last update timestamp |
| first_name | String | Customer first name |
| last_name | String | Customer last name |
| email | String | Customer email |

## Data Quality

The bronze-to-silver transformation performs the following data quality operations:

- **Null Handling:** Fills missing values with sensible defaults
- **Deduplication:** Removes duplicate customer records by customer_id
- **Calculated Fields:** Computes missing total_charges from monthly_charges × tenure
- **Schema Validation:** Enforces strict schema matching during JSON parsing
- **Partitioning:** Organizes data by year/month/day/hour for optimal querying in silver layer
- **Watermarking:** Handles late-arriving data with 10-minute watermark window

The silver-to-gold transformation performs additional business logic:
- Aggregations and feature engineering
- Data enrichment from external sources (if applicable)
- Business rule enforcement
- Data validation before loading to production database
## Monitoring

- **Bronze Layer:** Check Event Hub for incoming messages and consumer lag
- **Silver Layer:** Monitor data in ADLS Gen2 at: `abfss://[container]@[storage_account].dfs.core.windows.net/silver/customers/`
- **Checkpoints:** Review checkpoint files at: `abfss://[container]@[storage_account].dfs.core.windows.net/checkpoints/customers_stream/`
- **Gold Layer:** Verify data loaded into AWS database using standard database monitoring tools
- **Performance:** Monitor Spark job performance in Databricks or Spark UI

## Troubleshooting

- **Connection Issues:** Verify Event Hub connection string and ADLS credentials
- **Data Loss:** Check `failOnDataLoss: false` setting (production should use checkpoint recovery)
- **Late Data:** Adjust watermark window from default "10 minutes" if needed
- **Performance:** Tune `processingTime` trigger interval based on data volume

## Next Steps

After data lands in the silver layer:
1. Transform and enrich data using `silver_to_postgres.ipynb`
2. Load into AWS database (gold layer) for model training and business queries
3. Generate aggregated metrics for reporting and analytics
4. Use gold layer data for ML model training and inference

