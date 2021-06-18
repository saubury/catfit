from twython import Twython
import random
from auth import (
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)

twitter = Twython(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)

messages = [
    "Hello World",
    "Hi there",
    "What's up?",
    "How's it going?",
    "Have you been here before?",
    "I'm hungry",
    "Time for a nap",
    "Yes, I'm eating",
]

message = random.choice(messages)
image = open('image.jpg', 'rb')
response = twitter.upload_media(media=image)
media_id = [response['media_id']]
twitter.update_status(status=message, media_ids=media_id)
print("Tweeted: " + message)
