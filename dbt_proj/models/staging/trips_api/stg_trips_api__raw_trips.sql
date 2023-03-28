with

source as (

    select * from {{ source('trips_api', 'raw_trips') }}

),

final as (

    select * from source

)

select * from final