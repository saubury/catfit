cat X | kafka-console-producer --bootstrap-server localhost:9092 --topic debug_log

CREATE STREAM debug_stream_raw (event_date varchar, cat_weight double, food_weight double) WITH (kafka_topic='debug_log', value_format='json');

create stream weight_stream_trans with (timestamp='event_ts', value_format='avro') as select 'snowy' as cat_name, stringtotimestamp(event_date, 'dd/MM/yyyy HH:mm:ss') as event_ts, event_date, cat_weight, food_weight from debug_stream ;

create table cat_weight_table as select min(event_ts) as ts_min, max(event_ts) as ts_max, min(cat_weight) as cat_weight_min, count(*) as cnt, cat_name from  weight_stream_trans window session (600 seconds) group by cat_name; 

select  timestamptostring(windowstart, 'dd/MM/yyyy HH:mm:ss') as win_start, timestamptostring(windowend, 'dd/MM/yyyy HH:mm:ss') as win_end, cat_weight_min, cnt from cat_weight_table where cat_name = 'snowy';


SET 'auto.offset.reset'='earliest';

select * from debug_stream emit changes limit 10;


create stream weight_stream_transformed with (timestamp='event_ts', value_format='avro') as select event_ts, cat_name, event_date, cat_weight, food_weight from weight_stream;

