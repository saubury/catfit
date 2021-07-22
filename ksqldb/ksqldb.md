
## Start Kafka and ksqlDB

```
confluent local services start
```

## Populate some data
Create a topic and populate

```
cd ksqldb

kafka-topics --bootstrap-server localhost:9092 --create --partitions 1 --replication-factor 1 --topic debug_log

cat debug_log.txt | kafka-console-producer --bootstrap-server localhost:9092 --topic debug_log
```

## Run ksqlDB

Start ksqlDB CLI with `ksql`

```
run script 'catfit.sql'
```

Followed by this query

```
select  timestamptostring(windowstart, 'dd/MM/yyyy HH:mm:ss') as win_start
, timestamptostring(windowend, 'dd/MM/yyyy HH:mm:ss') as win_end
, (windowend-windowstart) / 1000 as eat_seconds
, round(cat_weight_avg) as cat_weight_grams
, round(food_weight_max - food_weight_min) as food_eaten_grams
, cnt 
from cat_weight_table 
where cat_name = 'snowy';
```

## Results
You should end up with something like this

```
+---------------------+---------------------+---------------------+---------------------+---------------------+
|WIN_START            |WIN_END              |EAT_SECONDS          |CAT_WEIGHT_GRAMS     |FOOD_EATEN_GRAMS     |
+---------------------+---------------------+---------------------+---------------------+---------------------+
|20/07/2021 06:23:40  |20/07/2021 06:35:53  |733                  |6002                 |57                   |
|20/07/2021 07:37:29  |20/07/2021 07:47:12  |583                  |6048                 |67                   |
|20/07/2021 10:41:14  |20/07/2021 10:51:49  |635                  |6038                 |23                   |
|20/07/2021 13:50:32  |20/07/2021 13:50:59  |27                   |6070                 |4                    |
|20/07/2021 17:09:35  |20/07/2021 17:24:41  |906                  |6027                 |40                   |
```