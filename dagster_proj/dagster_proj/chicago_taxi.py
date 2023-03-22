import json
import os
import requests
import base64

import pandas as pd
from google.oauth2.service_account import Credentials
from google.cloud import storage, bigquery
from dagster import DailyPartitionsDefinition, asset


APP_TOKEN = os.getenv('EVERGREEN_DL_APP_TOKEN')

AUTH_FILE = "./gcp_creds.json"
with open(AUTH_FILE, "w") as f:
    json.dump(json.loads(base64.b64decode(os.getenv("GCP_CREDS_JSON_CREDS_BASE64"))), f)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = AUTH_FILE

# GCP 
creds = Credentials.from_service_account_file(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
bucket_name = 'chicago_taxi_1'
storage_client = storage.Client(credentials=creds)
bucket = storage_client.get_bucket(bucket_name)
bigquery_client = bigquery.Client(credentials=creds)

# Set BigQuery table and dataset information
project_id = 'horizons-learning'
dataset_id = 'chicago_taxi'
table_id = 'raw_trips'


@asset(partitions_def=DailyPartitionsDefinition(start_date="2022-01-01"))
def trips_to_gcs(context) -> str:
    partition_date_str = context.asset_partition_key_for_output()
    url = 'https://data.cityofchicago.org/resource/wrvz-psew.json'
    headers = {'X-App-token':APP_TOKEN}

    offset = 0
    batch_size = 1000
    daily_data = []

    while True:
        print(f'Entered_loop_with_offset: {offset}')
        td = partition_date_str
        where = f"$where=trip_start_timestamp>='{td}T00:00:00.000'%20AND%20trip_start_timestamp<='{td}T23:59:59.999'"
        params = f"{where}&$limit={batch_size}&$order=trip_id&$offset={offset}"
        response = requests.get(f"{url}?{params}", headers=headers, timeout=60)
        
        # Check if the response is successful
        if response.status_code == 200:
            # Process the data in the response
            data = response.json()
            daily_data += data

            assert len(response.json()) != 0, f'There is no data for {td}'
            # If the number of items in the response is less than the batch size,
            # we have reached the end of the data and can break out of the loop
            if len(response.json()) < batch_size:
                file_name = f'{td}_trips'
                json_data = json.dumps(daily_data)
                blob = bucket.blob(file_name)
                blob.upload_from_string(json_data)
                print(f"File '{file_name}' saved to GCS")
                break

            # Increment the offset by the batch size to fetch the next batch of data
            offset += batch_size
        else:
            # TODO: add meaningful error message
            raise ConnectionRefusedError('Failed to get a successful response')
    return 'ok'
    
@asset(partitions_def=DailyPartitionsDefinition(start_date="2022-01-01"))
def trips_to_bq(context, trips_to_gcs) -> None:
    partition_date_str = context.asset_partition_key_for_output()
    # Download JSON data from GCS
    file_name = f'{partition_date_str}_trips'
    blob = bucket.blob(file_name)
    json_data = blob.download_as_string()

    # Parse JSON data
    data = json.loads(json_data)
    dtypes = {
        'pickup_centroid_location': str,
        'dropoff_centroid_location': str
    }
    df = pd.DataFrame(data=data).astype(dtypes)

    job_config = bigquery.LoadJobConfig(
        create_disposition='CREATE_IF_NEEDED',
        write_disposition='WRITE_APPEND'
    )

    # Load to BQ
    destination_table = f'{project_id}.{dataset_id}.{table_id}'
    job = bigquery_client.load_table_from_dataframe(df, 
                                                    destination_table, 
                                                    job_config=job_config)  

    job.result()  
    print(f"Loaded successfully: {len(df)} rows")

