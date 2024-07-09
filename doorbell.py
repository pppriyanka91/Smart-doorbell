from picamera import PiCamera
from gpiozero import Button
import datetime
from time import sleep
from datetime import datetime
from signal import pause
import os
from google.cloud import pubsub_v1
import numpy as np
import argparse
import json
import time
from google.cloud import vision
import jwt
import paho.mqtt.client as mqtt
import re
from gpiozero import LED


ssl_private_key_filepath = '/home/shanepriyanka/demo_private.pem'  #<ssl-private-key-filepath>'
ssl_algorithm = 'RS256'  #<algorithm>' # Either RS256 or ES256
root_cert_filepath = '/home/shanepriyanka/roots.pem'  #<root-certificate-filepath>'
project_id = 'jingye-zhang' #<GCP project id>'
gcp_location = 'europe-west1'  #<GCP location>'
registry_id = 'jingye.zhang'  #<IoT Core registry id>'
device_id = 'jingye-device'  #<IoT Core device id>'
# end of user-variables
green = LED(17)
red =LED(18)
button = Button(1)
camera = PiCamera()




def picture():
    timestamp = datetime.now().isoformat()
    camera.capture('/home/shanepriyanka/friend.jpg')
    
    
def storage():
    from google.cloud import storage
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'jingye-zhang-2ca0d3f5ff72.json'
    storage_client = storage.Client()
    #img = cv2.imread('try5.jpg')
    bucket_name = "jingye_zhang"
    bucket = storage_client.get_bucket(bucket_name)
    picBlob = bucket.blob('friend.jpg')  #os.sys.argv[1])
    #print('/home/iotyana/GCP_Quick_Starts/' + os.sys.argv[1])

    picBlob.upload_from_filename('/home/shanepriyanka/friend.jpg')  #/home/iotyana/GCP_Quick_Starts/' + os.sys.argv[1])

    print("Bucket {bucket.name} created.")
    
def summarize(message):
    data = message.data.decode("utf-8")
    attributes = message.attributes

    event_type = attributes["eventType"]
    bucket_id = attributes["bucketId"]
    object_id = attributes["objectId"]
    generation = attributes["objectGeneration"]
    description = (
        "\tEvent type: {event_type}\n"
        "\tBucket ID: {bucket_id}\n"
        "\tObject ID: {object_id}\n"
        "\tGeneration: {generation}\n"
    ).format(
        event_type=event_type,
        bucket_id=bucket_id,
        object_id=object_id,
        generation=generation,
    )

    if "overwroteGeneration" in attributes:
        description += f"\tOverwrote generation: {attributes['overwroteGeneration']}\n"
    if "overwrittenByGeneration" in attributes:
        description += f"\tOverwritten by generation: {attributes['overwrittenByGeneration']}\n"

    payload_format = attributes["payloadFormat"]
    if payload_format == "JSON_API_V1":
        object_metadata = json.loads(data)
        size = object_metadata["size"]
        content_type = object_metadata["contentType"]
        metageneration = object_metadata["metageneration"]
        description += (
            "\tContent type: {content_type}\n"
            "\tSize: {object_size}\n"
            "\tMetageneration: {metageneration}\n"
        ).format(
            content_type=content_type,
            object_size=size,
            metageneration=metageneration,
        )
    return description


def poll_notifications():
    project = 'jingye-zhang'
    subscription_name= 'my-subscription'
    """Polls a Cloud Pub/Sub subscription for new GCS events for display."""
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        project, subscription_name
    )

    def callback(message):
        print(f"Received message:\n{summarize(message)}")
        message.ack()

    subscriber.subscribe(subscription_path, callback=callback)

    print(f"Listening for messages on {subscription_path}")
    

           
def detect_faces_uri(uri):
    """Detects faces in the file located in Google Cloud Storage or the web."""
    
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = uri

    response = client.face_detection(image=image)
    faces = response.face_annotations

    # Names of likelihood from google.cloud.vision.enums
    likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                       'LIKELY', 'VERY_LIKELY')
    print('Faces:')

    for face in faces:
        print('anger: {}'.format(likelihood_name[face.anger_likelihood]))
        print('joy: {}'.format(likelihood_name[face.joy_likelihood]))
        print('surprise: {}'.format(likelihood_name[face.surprise_likelihood]))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in face.bounding_poly.vertices])

        print('face bounds: {}'.format(','.join(vertices)))
        
        likelihood = face.joy_likelihood
        #print("likelihood value = " , likelihood.value)  #----> likelihood.xxx
        #print(type(likelihood.value))  #---->int
        
        #a = str(likelihood.value)
        a = likelihood.value
        if a == 3 :
             msg = "joy"
        elif a == 4:
            msg = "joy"
        elif a == 5:
            msg = "joy"
        elif a == 1:
             msg = "anger"
        elif a == 2:
            msg = "anger"
        print(msg)
        return msg
        
        
    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    
def respondToMsg():
    msg = detect_faces_uri(imageFile)
   # return ''
    if msg == "joy":
        red.off() # sense.clear(255,0,0)
        green.on()
        sleep(1)
        #print(" green on")
    elif msg == "anger":
        #sense.clear(0,255,0)
        red.on( )
        green.off()
        sleep(1)
        #print("red on")


while True:
    print('Ring the bell...')
    button.wait_for_press()
    camera.start_preview()
    picture()
    sleep(5)
    camera.stop_preview()
    storage()
    sleep(5)
    poll_notifications()
    imageFile = "gs://jingye_zhang/friend.jpg" 
    detect_faces_uri(imageFile)
    respondToMsg()
  

