import json

from sodapy import Socrata
from dagster import DailyPartitionsDefinition, asset


SOCRATA_APP_TOKEN = "redacted"


@asset(partitions_def=DailyPartitionsDefinition(start_date="2023-02-28"))
def test_taxi_daily_partition(context) -> None:
    partition_date_str = context.asset_partition_key_for_output()
    client = Socrata("data.cityofchicago.org", SOCRATA_APP_TOKEN, timeout=600)
    query = f"date_trunc_ymd(trip_start_timestamp)='{partition_date_str}T00:00:00.000'"
    results = client.get("wrvz-psew", where=query, limit=50000)
    with open(f"temp_taxi/taxi_{partition_date_str}.json", "w") as f:
        json.dump(results, f)

