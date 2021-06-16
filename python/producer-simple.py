#!/usr/bin/env python

from confluent_kafka import Producer, KafkaError
import json
import config



if __name__ == '__main__':

    topic = 'test3'
    producer_conf = {
    'bootstrap.servers': config.bootstrap_servers, 
    'sasl.username': config.sasl_username, 
    'sasl.password': config.sasl_password,
    'security.protocol': 'SASL_SSL', 
    'sasl.mechanisms': 'PLAIN'
    }

    producer = Producer(producer_conf)


    # a Python object (dict):
    x = {"name": "Simon A", "age": 20, "city": "Sydney" }

    record_value = json.dumps(x)
    producer.produce(topic,  value=record_value)
    producer.poll(0)
    producer.flush()

