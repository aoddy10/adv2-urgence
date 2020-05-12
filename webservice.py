# Fall detector webservice
#
# Kim Salmi, kim.salmi(at)iki(dot)fi
# http://tunn.us/arduino/falldetector.php
# License: GPLv3

import requests
import json


class Webservice():

    def __init__(self):
        # set api url and request token
        self.url = 'https://us-central1-urgence-7232b.cloudfunctions.net/api/v1/'
        self.headers = {'Authorization': 'Bearer 2c19b8e18579401fb1d4032b8d1b3ad6',
                        'Content-Type': 'application/json'}
        self.data = ''

    def alarm(self, camera_id, image_binary):
        payload = {'camera_id': camera_id, 'image_binary': image_binary}
        response = requests.post(
            self.url + 'camera', data=json.dumps(payload), headers=self.headers)  # use json.dumps to send data in json format
        print(response)

    def checkVersion(self, device_id):
        payload = {'device_id': device_id}
        response = requests.post(
            self.url + 'version', data=json.dumps(payload), headers=self.headers)  # use json.dumps to send data in json format
        return response.json()
