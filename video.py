import time
import cv2
import person
import settings
import webservice
from datetime import datetime
import base64
from PIL import Image, ImageFile
import math
import subprocess
import json
import urllib
from zipfile import ZipFile
import os

debug = 0


class Video:

    def __init__(self, source):
        self.camera = cv2.VideoCapture(source)
        self.backgroundFrame = None
        self.start = time.time()
        self.settings = settings.Settings()
        self.persons = person.Persons(
            self.settings.movementMaximum, self.settings.movementMinimum, self.settings.movementTime)
        self.start = time.time()
        self.webservice = webservice.Webservice()
        self.errorcount = 0
        self.alertLog = []
        self.frameCount = 1

    def nextFrame(self):
        grabbed, self.frame = self.camera.read()
        if not grabbed:  # eof
            self.destroyNow()
        self.convertFrame()

    def showFrame(self):
        if debug:
            cv2.imshow("Thresh", self.thresh)
            cv2.imshow("backgroundFrame", self.backgroundFrame)
            cv2.imshow("frameDelta", self.frameDelta)
        cv2.imshow("Feed", self.frame)

    def destroyNow(self):
        self.camera.release()
        cv2.destroyAllWindows()

    def testDestroy(self):
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            self.destroyNow()
            return 1
        else:
            return 0

    def resetbackgroundFrame(self):
        grabbed, self.frame = self.camera.read()
        self.convertFrame()
        self.backgroundFrame = self.currentFrame
        self.persons = person.Persons(
            self.settings.movementMaximum, self.settings.movementMinimum, self.settings.movementTime)
        self.frameCount = 1
        print('resetbackgroundFrame')

    def testBackgroundFrame(self):
        key = cv2.waitKey(1) & 0xFF
        if key == ord("n"):
            self.backgroundFrame = None
        if self.backgroundFrame is None:
            self.resetbackgroundFrame()

    def testSettings(self):
        key = cv2.waitKey(1) & 0xFF
        if key == ord("0"):
            self.settings.minArea += 50
            print("minArea: ", self.settings.minArea)
        if key == ord("9"):
            self.settings.minArea -= 50
            print("minArea: ", self.settings.minArea)
        if key == ord("8"):
            self.settings.dilationPixels += 1
            print("dilationPixels: ", self.settings.dilationPixels)
        if key == ord("7"):
            self.settings.dilationPixels -= 1
            print("dilationPixels: ", self.settings.dilationPixels)
        if key == ord("6"):
            self.settings.thresholdLimit += 1
            print("thresholdLimit: ", self.settings.thresholdLimit)
        if key == ord("5"):
            self.settings.thresholdLimit -= 1
            print("thresholdLimit: ", self.settings.thresholdLimit)
        if key == ord("4"):
            self.settings.movementMaximum += 1
            print("movementMaximum: ", self.settings.movementMaximum)
        if key == ord("3"):
            self.settings.movementMaximum -= 1
            print("movementMaximum: ", self.settings.movementMaximum)
        if key == ord("2"):
            self.settings.movementMinimum += 1
            print("movementMinimum: ", self.settings.movementMinimum)
        if key == ord("1"):
            self.settings.movementMinimum -= 1
            print("movementMinimum: ", self.settings.movementMinimum)
        if key == ord("o"):
            if self.settings.useGaussian:
                self.settings.useGaussian = 0
                print("useGaussian: off")
                self.resetbackgroundFrame()
            else:
                self.settings.useGaussian = 1
                print("useGaussian: on")
                self.resetbackgroundFrame()
        if key == ord("+"):
            self.settings.movementTime += 1
            print("movementTime: ", self.settings.movementTime)
        if key == ord("p"):
            self.settings.movementTime -= 1
            print("movementTime : ", self.settings.movementTime)

    def updateBackground(self):
        alpha = (1.0/self.frameCount)
        self.backgroundFrame = cv2.addWeighted(
            self.currentFrame, alpha, self.backgroundFrame, 1.0-alpha, 0)
        self.frameCount += 1

    def convertFrame(self):
        r = 750.0 / self.frame.shape[1]
        dim = (750, int(self.frame.shape[0] * r))
        self.frame = cv2.resize(self.frame, dim, interpolation=cv2.INTER_AREA)
        self.currentFrame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        if self.settings.useGaussian:
            self.currentFrame = cv2.GaussianBlur(
                self.currentFrame, (self.settings.gaussianPixels, self.settings.gaussianPixels), 0)

    def compare(self):
        # difference between the current frame and backgroundFrame
        self.frameDelta = cv2.absdiff(self.backgroundFrame, self.currentFrame)
        self.thresh = cv2.threshold(
            self.frameDelta, self.settings.thresholdLimit, 255, cv2.THRESH_BINARY)[1]
        self.thresh = cv2.dilate(
            self.thresh, None, iterations=self.settings.dilationPixels)  # dilate thresh
        (_, contours, _) = cv2.findContours(self.thresh.copy(),
                                            cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # find contours

        self.persons.tick()

        detectStatus = "idle"

        for contour in contours:
            if cv2.contourArea(contour) < self.settings.minArea:
                continue

            (x, y, w, h) = cv2.boundingRect(contour)

            if self.thresh.shape[1] < w+50 and self.thresh.shape[0] < h+50:
                self.newLightconditions()
                continue

            person = self.persons.addPerson(x, y, w, h)
            color = (0, 255, 0)
            if person.alert:
                color = (0, 0, 255)
                cv2.line(self.frame, (x, y), (x + w, y + h), color, 2)
                cv2.line(self.frame, (x + w, y), (x, y + h), color, 2)
                detectStatus = "Alarm, not moving"
                if not person.alarmReported:
                    print('Not moving detected')
                    person.alarmReported = 1

                    # capture image
                    imageFileLocation = self.captureImage()

                    predictResult = self.getPrediction(imageFileLocation)
                    # predictResult = self.getPrediction('./images/test.jpg')

                    if float(predictResult) > 0.9:
                        # get camera_id
                        device_id = self.getSerial()
                        # reduce image size and encode to base64
                        self.reduceImageSize(imageFileLocation)
                        imageBase64 = self.convertImageToBase64(
                            imageFileLocation)

                        # send image to API
                        print('send alert to api with image data and device id')
                        self.webservice.alarm(device_id, imageBase64)

                    # delete file in images folder
                    os.remove(imageFileLocation)

            cv2.rectangle(self.frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(self.frame, "{}".format(cv2.contourArea(contour)),
                        (x, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 1)
            cv2.putText(self.frame, "{} : {}".format(
                person.id, person.lastmoveTime), (x, y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 1)

        # Hud + fps
        if debug:
            self.end = time.time()
            seconds = self.end - self.start
            fps = round((1 / seconds), 1)
            self.start = time.time()

            cv2.putText(self.frame, "Status: {}".format(detectStatus),
                        (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 140, 255), 1)
            cv2.putText(self.frame, "FPS: {}".format(fps), (400, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 140, 255), 1)

    def newLightconditions(self):
        self.errorcount += 1
        if self.errorcount > 10:
            time.sleep(1.0)
            self.resetbackgroundFrame()
            self.errorcount = 0

    # capture image
    def captureImage(self):
        fileLocation = ""
        while(True):
            ret, frame = self.camera.read()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

            # cv2.imshow('frame', rgb) # show capture image

            now = datetime.now()
            # create file location
            fileLocation = './images/' + now.strftime("%Y%m%d-%H%M%S") + '.jpg'
            out = cv2.imwrite(fileLocation, frame)
            break
        return fileLocation

    # convert image to base64
    def convertImageToBase64(self, imageFileLocation):
        with open(imageFileLocation, "rb") as img_file:
            my_string = base64.b64encode(img_file.read())
        return my_string.decode('utf-8')

    # get raspberry pi's cpuid
    def getSerial(self):
        # Extract serial from cpuinfo file
        cpuserial = "0000000000000000"
        try:
            f = open('/proc/cpuinfo', 'r')
            for line in f:
                if line[0:6] == 'Serial':
                    cpuserial = line[10:26]
            f.close()
        except:
            cpuserial = "ERROR000000000"

        return cpuserial

    # resize image to 250px
    def reduceImageSize(self, imageFileLocation):
        pic = imageFileLocation
        im = Image.open(pic)
        width, height = im.size

        resizeRatio = 250/width

        # if width and height more than 1000, do resize
        if width > 1000 or height > 1000:
            width = width*resizeRatio
            height = height*resizeRatio
        im = im.resize((int(math.floor(width)), int(
            math.floor(height))), Image.ANTIALIAS)
        try:
            im.save(pic, optimize=True, quality=75)
        except IOError:
            ImageFile.MAXBLOCK = width * height
            im.save(pic, optimize=True, quality=75)

    # get prediction from ML
    def getPrediction(self, sourceFileLocation):
        # ML model location
        modelPb = "tensorflow-for-poets-2/tf_files/retrained_graph.pb"
        modelLabels = "tensorflow-for-poets-2/tf_files/retrained_labels.txt"

        # create command
        cmd = "python3 -m tensorflow-for-poets-2.scripts.label_image --image=" + \
            sourceFileLocation + " --graph=" + modelPb + " --labels=" + modelLabels

        # run command
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

        (output, err) = p.communicate()

        p_status = p.wait()

        # print "Command output : ", output
        print(output)
        return output

    def checkUpdateVersion(self):
        print('Check to update software.')

        device_id = self.getSerial()
        requireUpdateDetail = self.webservice.checkVersion(device_id)

        # check if it need to update
        if requireUpdateDetail["error"] == False and requireUpdateDetail["require_update"] == True:
            print('Need to update new version: ' +
                  requireUpdateDetail["new_version"])

            # load file for update
            updateFile_url = requireUpdateDetail["file_url"]

            # download file
            print('download file from server...')
            self.downloadFile(updateFile_url)

            # unzip update.zip and extract to ML folder
            print('Unzip update file and extract to ML location...')
            self.extractUpdateFile()

            # update software verion in database
            print('Updated software version on database...')
            updateResponse = self.webservice.updateVersion(
                device_id, requireUpdateDetail["new_version"])
            if updateResponse["error"] == False:
                print('Update vesion on database....successful.')
            else:
                print('Update vesion on database....fail.')

        else:
            print("Don't have new version to update.")

    def downloadFile(self, url):
        file_name = 'update.zip'
        u = urllib.urlopen(url)
        f = open(file_name, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print "Downloading: %s Bytes: %s" % (file_name, file_size)

        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d  [%3.2f%%]" % (
                file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            print status,

        print('')
        print('Finish download')
        f.close()
        return True

    def extractUpdateFile(self):
        zf = ZipFile('update.zip', 'r')
        zf.extractall('./tensorflow-for-poets-2/tf_files/')
        zf.close()
        print('Finish extract and update file in ML location.')
