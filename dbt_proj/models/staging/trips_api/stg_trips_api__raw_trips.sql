with

source as (

    select * from {{ source('trips_api', 'raw_trips') }}

),

final as (

    select
        trip_id,
        taxi_id,
        parse_timestamp('%Y-%m-%dT%H:%M:%E*S', trip_start_timestamp) as trip_start_dt,
        parse_timestamp('%Y-%m-%dT%H:%M:%E*S', trip_end_timestamp) as trip_end_dt,
        safe_cast(trip_seconds as float64) as trip_duration_seconds,
        safe_cast(trip_miles as float64) as trip_length_miles,
        safe_cast(pickup_community_area as int) as pickup_community_area,
        safe_cast(dropoff_community_area as int) as dropoff_community_area,
        safe_cast(fare as float64) as fare_usd,
        safe_cast(tips as float64) as tips_usd,
        safe_cast(tolls as float64) as tolls_usd,
        safe_cast(extras as float64) as extra_charges_usd,
        safe_cast(trip_total as float64) as trip_total_cost_usd,
        payment_type,
        company as taxi_company,
        safe_cast(pickup_centroid_latitude as float64) as pickup_centroid_latitude,
        safe_cast(pickup_centroid_longitude as float64) as pickup_centroid_longitude,
        safe_cast(dropoff_centroid_latitude as float64) as dropoff_centroid_latitude,
        safe_cast(dropoff_centroid_longitude as float64) as dropoff_centroid_longitude,
        pickup_census_tract,
        dropoff_census_tract
    from source

)

select * from final