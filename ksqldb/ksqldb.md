cat X | kafka-console-producer --bootstrap-server localhost:9092 --topic debug_log

run script 'catfit.sql'

select  timestamptostring(windowstart, 'dd/MM/yyyy HH:mm:ss') as win_start
, timestamptostring(windowend, 'dd/MM/yyyy HH:mm:ss') as win_end
, cat_weight_min
, cat_weight_avg
, cat_weight_max
, food_weight_min
, food_weight_max
, food_weight_max - food_weight_min as food_eaten
, cnt 
from cat_weight_table 
where cat_name = 'snowy';
