# Take picture code goes here

from __future__ import print_function
import pickle
import os.path
import requests
import pymysql
import datetime
from datetime import datetime, time
import numpy as py
from time import sleep
from picamera import PiCamera
from PIL import Image
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']
TIME_PERIOD = 60
TOTAL_TIME = 300
DEFAULT_PHOTO_PATH = '/home/pi/Pictures/results/'
DB_HOST_NAME = None
DB_USER_NAME = None
# The password should ideally be stored on a file rather than in a string.
DB_PASSWORD = None
# The acceptable boundary for Computer Vision to estimate a human object.
# 0.50 seemed to be an acceptable in testing, but change as needed. 
HUMAN_CONFIDENCE = 0.50




def main():
    print("Now beginning a new round of measurement...")
    while True:
        try:


            creds = None
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server()
                # Save the credentials for the next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)

            service = build('drive', 'v3', credentials=creds)

            # Call the Drive v3 API

            print("[DRIVE] Google Drive authenticated!")

            timestamp = datetime.now()
            photo_id = capturePhoto(str(timestamp))

            folderId = None

            file_metadata = {'name': str(timestamp) + ".jpg", 'parents': [folderId]}
            media = MediaFileUpload(photo_id,
                                mimetype='image/jpeg')
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print("File captured and uploaded to Google Drive.")
            break
        except Exception as err:
            print("Cloud service appears to have broke. Retrying...")
            pass

    people_no = getOccCount(photo_id)
    avgCo2 = generateRooms()
    meanCo2 = py.mean(avgCo2)

    if people_no > 0:
        room_occupied = True
    else:
        room_occupied = False
    print('[DATABASE] Backing up results to database. Please wait.')

    # converts numpy floats into translatable generic system floats
    pymysql.converters.encoders[py.float64] = pymysql.converters.escape_float
    pymysql.converters.conversions = pymysql.converters.encoders.copy()
    pymysql.converters.conversions.update(pymysql.converters.decoders)

    # Save the results to the Database.

    while True:
        try:
            connection = pymysql.connect(host=DB_HOST_NAME,
                                         user=DB_USER_NAME,
                                         password=DB_PASSWORD,
                                         db='results',
                                         charset='utf8mb4',
                                         cursorclass=pymysql.cursors.DictCursor)
            break
        except pymysql.OperationalError as err:
            print(err)
            pass

    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `entries` (`numberOfOccupants`, `isRoomOccupied`, `co2Level`, `timeDateRecorded`) " \
                  "VALUES (%s,%s,%s,%s)"
            cursor.execute(sql, (people_no, room_occupied, meanCo2, timestamp))
            connection.commit()
    finally:
        connection.close()

    print("[MEASUREMENT] Results were saved successfully! Sleeping until next measurement...")


def getOccCount(image_path):
    # The subscriber key as provided by Azure Computer Vision. You MUST set up a Cognitive Services account first.
    sub_key = None

    image_data = open(image_path, "rb").read()
    headers = {'Ocp-Apim-Subscription-Key': sub_key,
               'Content-Type': 'application/octet-stream'}
    vision_base_url = "https://uksouth.api.cognitive.microsoft.com/vision/v2.0/"
    analyze_url = vision_base_url + "detect"
    while True:
        try:
            res = requests.post(
                analyze_url, headers=headers, data=image_data)
            res.raise_for_status()
            results = res.json()
            break
        except requests.ConnectionError as err:
            pass
    object_list = results.get('objects')
    occupantCount = 0
    for detected_objects in object_list:
        if detected_objects.get('object') == 'person' and detected_objects.get('confidence') > HUMAN_CONFIDENCE:
            occupantCount = occupantCount + 1

    print("The total number of people detected are... " + str(occupantCount))
    return occupantCount


def generateRooms():
    print('[MEASUREMENT] Now starting measurement. This will take roughly 5 minutes.')
    totalTimer = TOTAL_TIME
    accResults = []
    occupancyCount = []

    co2Results = requests.get("https://api.usb.urbanobservatory.ac.uk/api/v2/sensors/feed/room-3-032/co2")
    latestCO2Val = co2Results.json().get('timeseries')[0].get('latest').get('value')

    while totalTimer > 0:
        try:
            co2Results = requests.get("https://api.usb.urbanobservatory.ac.uk/api/v2/sensors/feed/room-3-032/co2")
        except requests.ConnectionError as err:
            print("URL appears to not work. Your internet may be busted.")
        latestCO2Val = co2Results.json().get('timeseries')[0].get('latest').get('value')
        sleep(TIME_PERIOD)
        totalTimer = totalTimer - TIME_PERIOD
        print("[MEASUREMENT] Captured CO2 value. Beginning next run.")
        accResults.append(latestCO2Val)

    return accResults


def capturePhoto(timestamp):
    with PiCamera() as camera:
        camera.resolution = (1024, 768)
        sleep(2)
        camera.capture(DEFAULT_PHOTO_PATH + timestamp + '.jpg')
        photo = Image.open(DEFAULT_PHOTO_PATH+timestamp+'.jpg')
        photo_corrected = photo.rotate(180)
        photo_corrected.save(DEFAULT_PHOTO_PATH+timestamp+'.jpg')
        print("[PICAM] - Captured image!" + DEFAULT_PHOTO_PATH + timestamp + ".jpg")
    pass

    return DEFAULT_PHOTO_PATH + timestamp + '.jpg'


# Time method created by Joe Holloway - https://stackoverflow.com/a/10048290
def is_time_between(begin_time, end_time, check_time=None):
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else:
        return check_time >= begin_time or check_time <= end_time


if __name__ == '__main__':
    while True:
        while is_time_between(time(9, 30), time(18, 30)) and datetime.today().weekday() < 5:
            main()
            sleep(1200)
