import video
import time
import sys

video = video.Video(0)
time.sleep(1.0)  # autofocus and autosaturation
video.nextFrame()
video.testBackgroundFrame()

isRequireUpdateCheck = True  # use for indicate that need to check update or not

while 1:
    # check update version
    if isRequireUpdateCheck == True:
        video.checkUpdateVersion()
        isRequireUpdateCheck = False

    video.nextFrame()
    video.testBackgroundFrame()
    video.updateBackground()
    video.compare()
    # video.showFrame()
    video.testSettings()
    if video.testDestroy():
        sys.exit()
