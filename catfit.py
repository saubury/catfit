import re
import argparse
import time
import sys
import RPi.GPIO as GPIO
from datetime import datetime
from confluent_kafka import Producer, KafkaError
import json
import config
from picamera import PiCamera
from twython import Twython
import random
import os
import paho.mqtt.publish as publish
from catimage import create_image


sys.path.insert(1, './hx711py')
from hx711 import HX711


# Settings
demo_file_path = 'example.out'
output_file='/home/pi/git/catfit/catfit.out'
image_dir = '/home/pi/git/catfit/photos'
cat_weight_min = 4500
cat_weight_max = 6100
referenceUnit_A = 22.839
referenceUnit_B = -1092.8
cat_depart_threshold_sec = 10
GPIO_A_DT = 17
GPIO_A_SCK = 27
GPIO_B_DT = 5
GPIO_B_SCK = 6

# Globals
cat_was_on_scale = False
cat_entered_scale_date = datetime.now()
cat_lastseen_date = datetime.now()
last_photo_date = datetime.now()
food_start_weight = 0
cat_weight_sample_total = 0
cat_weight_sample = 0
pict_base_list = []

# Kafka Producer
producer_conf = {
'bootstrap.servers': config.bootstrap_servers, 
'sasl.username': config.sasl_username, 
'sasl.password': config.sasl_password,
'security.protocol': 'SASL_SSL', 
'sasl.mechanisms': 'PLAIN'
}

# MQTT Producer
mqtt_broker=config.mqtt_broker
mqtt_port=config.mqtt_port
mqtt_auth = {'username':config.mqtt_username, 'password':config.mqtt_password}
mqtt_topic='catfit/foodstation'

# Twitter
twitter = Twython(
    config.consumer_key,
    config.consumer_secret,
    config.access_token,
    config.access_token_secret
)

producer = Producer(producer_conf)


def cleanAndExit():
    do_print("Cleaning...")
    GPIO.cleanup()
    do_print("Bye!")
    sys.exit()

def do_scale():
    hx_a = HX711(GPIO_A_DT, GPIO_A_SCK)
    hx_b = HX711(GPIO_B_DT, GPIO_B_SCK)

    hx_a.set_reading_format("MSB", "MSB")
    hx_b.set_reading_format("MSB", "MSB")

    hx_a.set_reference_unit(referenceUnit_A)
    hx_a.reset()
    hx_a.tare()
    do_print("Tare A done! Add weight now...")

    hx_b.set_reference_unit(referenceUnit_B)
    hx_b.reset()
    # hx_b.tare()
    do_print("Tare B done! Add weight now...")

    while True:
        try:
            val_cat = hx_a.get_weight(GPIO_A_DT)
            val_food = hx_b.get_weight(GPIO_B_DT)

            # if (val_a > threshHold ):
            now = datetime.now()
            # print('{}    Cat:{:,.0f}  Food:{:,.0f}'.format(now.strftime("%d/%m/%Y %H:%M:%S"), val_cat, val_food))
            do_update(now, val_cat, val_food)
            do_kafka_produce(now, val_cat, val_food)

            hx_a.power_down()
            hx_a.power_up()
            hx_b.power_down()
            hx_b.power_up()
            time.sleep(0.1)

        except (KeyboardInterrupt, SystemExit):
            cleanAndExit()


def do_kafka_produce(event_date, cat_weight, food_weight):
    if cat_weight_min <= cat_weight <= cat_weight_max:
    # Cat is on scale

        json_payload=json.dumps({"event_date": event_date.strftime("%d/%m/%Y %H:%M:%S"), "cat_weight": cat_weight, "food_weight": food_weight })
        producer.produce('debug_log',  value=json_payload  )
        producer.poll(0)
        producer.flush()

        producer.produce('cat_weight',  value=json.dumps({"event_date": event_date.strftime("%d/%m/%Y %H:%M:%S"), "cat_weight": cat_weight }))
        producer.poll(0)
        producer.flush()

        producer.produce('food_weight',  value=json.dumps({"event_date": event_date.strftime("%d/%m/%Y %H:%M:%S"), "food_weight": food_weight }))
        producer.poll(0)
        producer.flush()

        # MQTT Publish
        publish.single(topic=mqtt_topic, payload=json_payload, hostname=mqtt_broker, port=mqtt_port, auth=mqtt_auth)


def do_update(event_date, cat_weight, food_weight):
    global cat_was_on_scale
    global cat_entered_scale_date
    global food_start_weight
    global cat_weight_sample_total
    global cat_weight_sample 
    global cat_lastseen_date

    if cat_weight_min <= cat_weight <= cat_weight_max:
        # Cat is on scale
        if ( not cat_was_on_scale ):
            # Cat just stepped onto scale
            cat_entered_scale_date = event_date
            food_start_weight = food_weight

        cat_was_on_scale = True
        cat_lastseen_date = event_date
        cat_weight_sample_total = cat_weight_sample_total + cat_weight
        cat_weight_sample = cat_weight_sample + 1
        do_photo()
    else:
        # Cat is not on scale
        sec_since_cat_seen = (event_date - cat_lastseen_date).total_seconds()
        if ( cat_was_on_scale ):
            # Cat just left
            do_print('   cat left - duration {:,.0f}     RAW Duration:{}'.format(sec_since_cat_seen, event_date-cat_lastseen_date))
            cat_weight_avg = cat_weight_sample_total / cat_weight_sample
            # print('cat_weight_avg:{:,.0f}  cat_weight_sample_total:{} cat_weight_samples:{}'.format(cat_weight_avg, cat_weight_sample_total, cat_weight_sample))
            cat_weight_sample_total = 0
            cat_weight_sample = 0
            cat_was_on_scale = False
            eating_duration_sec = (event_date-cat_entered_scale_date).total_seconds()
            eaten_amount = food_start_weight - food_weight
            do_print('Cat departed,  From:{} To:{} FoodStart:{:,.0f} FoodEnd:{:,.0f} Duration:{} cat_weight_avg:{:,.0f} Seconds:{} Eaten:{}'.format(cat_entered_scale_date, event_date, food_start_weight, food_weight, event_date-cat_entered_scale_date, cat_weight_avg, eating_duration_sec, eaten_amount))
            do_image_and_tweet(eaten_amount, eating_duration_sec, cat_weight_avg)

def do_image_and_tweet(eaten_amount, eating_duration_sec, cat_weight_avg):
    global pict_base_list

    messages = [
        "Hello World.",
        "Hi there.",
        "What's up?",
        "How's it going?",
        "Yes, I may be over sharing.",
        "I'm hungry.",
        "Time for a nap.",
        "Hey.",
        "Time for an update.",
        "Tweet much?",
        "Yes, I'm eating.",
    ]

    if eaten_amount <= 0:
        # protect against negative values
        do_print('Negative food - skipped')
        return

    if eaten_amount > 50:
        # protect against large values
        do_print('Seemingly too much food - skipped')
        return

    if len(pict_base_list) == 0:
        # protect against no photo taken
        do_print('No photo - skipped')
        return

    if len(pict_base_list) == 1:
        # Only one photo; use it
        image_base_file = pict_base_list[0]
        do_print('Only one photo - using {}'.format(image_base_file))
    else:
        # Multiple photos; pick the 2nd last one
        image_base_file = pict_base_list[-2]
        do_print('Multiple photos - using {}'.format(image_base_file))

    # reset the list
    pict_base_list = []    

    # all good - now tweet
    tweet_image = '{}_t.jpg'.format(image_base_file)
    create_image('{}_a.jpg'.format(image_base_file), 
    '{}_b.jpg'.format(image_base_file),  
    tweet_image, 
    'Snowy ate {:,.0f}g of food\nover {:,.0f} seconds'.format(eaten_amount, eating_duration_sec))

    rand_message = random.choice(messages)
    tweet_message = '{} I just ate {:,.0f}g of food, over {:,.0f} seconds. I now weigh {:,.0f} grams. {} ???? #snowydata ??? https://link.medium.com/53QclBbWLhb'.format(rand_message, eaten_amount, eating_duration_sec, cat_weight_avg, datetime.now().strftime("%A at %I:%M %p"))
    do_tweet(tweet_message, tweet_image)

def do_filedemo():
    with open(demo_file_path) as file_handle:
        line = file_handle.readline()
        while line:
            line_parts=re.split(r'(?=[A-Z])', line.strip())
            event_date_text=line_parts[0].strip()
            event_date = datetime.strptime(event_date_text, '%d/%m/%Y %H:%M:%S')
            cat_weight=re.sub(r'[^0-9]', '', line_parts[1])
            food_weight=re.sub(r'[^0-9\-]', '', line_parts[2])
            do_update(event_date, int(cat_weight), int(food_weight))
            line = file_handle.readline()


def do_print(text):
    now = datetime.now()
    with open(output_file, "a") as file1:
        file1.write( '{}   {}\n'.format(now.strftime("%d/%m/%Y %H:%M:%S"), text) )

    # Now to stdout    
    print( '{}   {}'.format(now.strftime("%d/%m/%Y %H:%M:%S"), text), flush=True )

def do_photo(tweet_it=False):
    global last_photo_date
    now = datetime.now()
    sec_since_last_photo = (now - last_photo_date).total_seconds()

    # Protect against too many photos taken over a short length of time
    if (sec_since_last_photo > 10):
        last_photo_date = now
        do_photo_inner(tweet_it)

def do_photo_inner(tweet_it=False):
    global pict_base_list
    now = datetime.now()
    image_base_file = '{}/{}'.format(image_dir, now.strftime("%Y%m%d_%H%M%S"))
    image_file_a = '{}_a.jpg'.format(image_base_file)
    image_file_b = '{}_b.jpg'.format(image_base_file)
    pict_base_list.append(image_base_file)

    print('Photo - filename {}'.format(image_base_file))

    # Camera 1
    with PiCamera(resolution=(1280, 720)) as camera:
        # camera = PiCamera()
        camera.iso = 1600
        time.sleep(2)
        camera.capture(image_file_a)

    # Camera 2
    os.system('fswebcam --palette YUYV --resolution 640x480 --no-banner --quiet {}'.format(image_file_b))


def do_tweet(message, file_image):
    with open(file_image, 'rb') as image:
        response = twitter.upload_media(media=image)
        media_id = [response['media_id']]
        twitter.update_status(status=message, media_ids=media_id)
        do_print("Tweeted: " + message)

def main():
    parser = argparse.ArgumentParser(description='Cat monitor')
    parser.add_argument('--scale', help='capture values from scales', action='store_true')
    parser.add_argument('--photo', help='take a photo', action='store_true')
    parser.add_argument('--filedemo', help='run a demonstration from file', action='store_true')
    args = parser.parse_args()

    if args.filedemo:
        do_filedemo()
    elif args.photo:
        do_photo_inner()
    else:
        do_scale()        
    # else:
    #     parser.print_help()

if __name__ == '__main__':
    main()
