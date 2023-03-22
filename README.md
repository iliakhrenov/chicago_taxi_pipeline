# Data Pipeline: Chicago Taxi Trips

Building a end-to-end data pipeline to explore the taxi trips data from 2022-01-01

## Steps and Technologies
- Data Ingestion:
    - [City of Chicago API](https://dev.socrata.com/foundry/data.cityofchicago.org/wrvz-psew) as a data source 
    - Google Cloud Storage: to store the data pulled from API in JSON format
    - Google Big Query: the data is loaded from GCS and written into GBQ table
- Data Orchestration:
    - Dagster
 
 ### Data Ingestion
The data ingestion pipeline is defined as a DAG of two Dagster assets: `dagster_proj/chicago_taxi.py`. This DAG contains two assets:
- `trips_to_gcs`: loads data from API and writes it as a JSON file stored in Google Cloud Storage
- `trips_to_bq`: loads data from Google Cloud Storage and writes in into a Google BigQuery table

The pipeline is partitioned by day.