import time
import requests
import operator
import numpy as np
# from __future__ import print_function

_url_accent = 'https://api.projectoxford.ai/vision/v1/analyses'
_key_accent = '00ddd41708ea42b2b6afdc73b574d2d7'
_url_emotion = 'https://api.projectoxford.ai/emotion/v1.0/recognize'
_key_emotion = '36c531a3defc46c38518eec7da08488e'
_maxNumRetries = 10

caps_rgb = ['fff8dc', 'ffe4c4', 'faebd7']

def processRequest(json, data, headers, params,_url):
    """
    Helper function to process the request to Project Oxford

    Parameters:
    json: Used when processing images from its URL. See API Documentation
    data: Used when processing image read from disk. See API Documentation
    headers: Used to pass the key information and the data type request
    """

    retries = 0
    result = None

    while True:

        response = requests.request('post', _url, json=json, data=data, headers=headers, params=params)

        if response.status_code == 429:

            print("Message: %s" % (response.json()['error']['message']))

            if retries <= _maxNumRetries:
                time.sleep(1)
                retries += 1
                continue
            else:
                print('Error: failed after retrying!')
                break

        elif response.status_code == 200 or response.status_code == 201:

            if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
                result = None
            elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
                if 'application/json' in response.headers['content-type'].lower():
                    result = response.json() if response.content else None
                elif 'image' in response.headers['content-type'].lower():
                    result = response.content
        else:
            print("Error code: %d" % (response.status_code))
            print("Message: %s" % (response.json()['error']['message']))

        break

    return result


def get_rgb(color):

    return int(color[:2], 16), int(color[2:4], 16), int(color[4:], 16)


def get_color_diff(accent, curr):
    accent_red, accent_green, accent_blue = get_rgb(accent)
    curr_red, curr_green, curr_blue = get_rgb(curr)
    red = float(abs(float(accent_red) - float(curr_red))/255)
    green = float(abs(float(accent_green) - float(curr_green))/255)
    blue = float(abs(float(accent_blue) - float(curr_blue))/255)

    return float(((red + green + blue)*100)/3)


def return_top_n(accent, n):
    perc_closeness = list()
    for i in caps_rgb:
        perc_closeness.append(get_color_diff(accent, i))

    perc_closeness.sort()

    return perc_closeness[:n]


print return_top_n('fff888', 2)


#load cap data into list

f = open('caps.txt', 'r')
lines = f.readlines()

cap=[]

for line in lines:
    # URL direction to image
    urlImage = line

    # Computer Vision parameters
    params = { 'visualFeatures' : 'Color,Categories'}

    headers = dict()
    headers['Ocp-Apim-Subscription-Key'] = _key_accent
    headers['Content-Type'] = 'application/json'

    json = { 'url': urlImage }
    data = None

    result = processRequest( json, data, headers, params,_url_accent )
    tempcap=[]
    tempcap.append(line)
    tempcap.append( result['color']['accentColor'])
    cap.append(tempcap)

print cap


# Load raw image file into memory
pathToFileInDisk = r'C:\Users\prana\Documents\UB\job\Ceevee10\images\profilepic.jpg'
with open(pathToFileInDisk, 'rb') as f:
    data = f.read()

# Computer Vision parameters
params = {'visualFeatures': 'Color,Categories'}

headers = dict()
headers['Ocp-Apim-Subscription-Key'] = _key_accent
headers['Content-Type'] = 'application/octet-stream'

json = None

result = processRequest(json, data, headers, params,_url_accent)

print result['color']['accentColor']
headers['Ocp-Apim-Subscription-Key'] = _key_emotion
result = processRequest( json, data, headers, params,_url_emotion )

for currFace in result:
        faceRectangle = currFace['faceRectangle']
        currEmotion = max(currFace['scores'].items(), key=operator.itemgetter(1))[0]
        print currEmotion

