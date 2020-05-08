import video
import time
import sys

video = video.Video(0)
time.sleep(1.0)  # autofocus and autosaturation
video.nextFrame()
video.testBackgroundFrame()

while 1:
    video.nextFrame()
    video.testBackgroundFrame()
    video.updateBackground()
    video.compare()
    video.showFrame()
    video.testSettings()
    if video.testDestroy():
        sys.exit()
