# Fall detector video class
# Source: camera (int) or file (string)
#
#
# Kim Salmi, kim.salmi(at)iki(dot)fi
# http://tunn.us/arduino/falldetector.php
# License: GPLv3


import subprocess
import video


class Test:

    myVideo = video.Video(0)
    myVideo.getPrediction('images/test.jpg')
    # myVideo.getPrediction('images/collapsed.jpeg')
