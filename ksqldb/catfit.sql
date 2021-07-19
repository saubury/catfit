SET 'auto.offset.reset'='earliest';

CREATE STREAM debug_stream_raw (event_date varchar, cat_weight double, food_weight double) 
WITH (kafka_topic='debug_log', value_format='json');

create stream weight_stream
with (timestamp='event_ts', value_format='avro') 
as 
select 'snowy' as cat_name
, stringtotimestamp(event_date, 'dd/MM/yyyy HH:mm:ss') as event_ts
, event_date
, cat_weight
, food_weight 
from debug_stream_raw ;

create table cat_weight_table 
as 
select min(cat_weight) as cat_weight_min
, max(cat_weight) as cat_weight_max
, avg(cat_weight) as cat_weight_avg
, min(food_weight) as food_weight_min
, max(food_weight) as food_weight_max
, avg(food_weight) as food_weight_avg
, count(*) as cnt
, cat_name 
from  weight_stream 
window session (600 seconds) 
where food_weight < 1100 and cat_weight > 5800 and cat_weight < 6200
group by cat_name
having count(*) > 4; 
