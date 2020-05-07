
# current date and time

# camera = PiCamera()
# if need to rotation camera
# camera.rotation = 180

# # preview camera for 5 second
# camera.start_preview()  # start preview when use GUI
# for i in range(5):
#     sleep(2)  # stop 2 second and move next to next capture
#     now = datetime.now()
#     camera.capture('/home/pi/Urgence/images/image' +
#                    now.strftime("%Y%m%d-%H%M%S") + '.jpg')
# camera.stop_preview()  # stop preview when use GUI


# class RaspberryBoard():
#     def getserial():
#         # Extract serial from cpuinfo file
#         cpuserial = "0000000000000000"
#         try:
#             f = open('/proc/cpuinfo', 'r')
#             for line in f:
#             if line[0:6] == 'Serial':
#                 cpuserial = line[10:26]
#             f.close()
#         except:
#             cpuserial = "ERROR000000000"

#         return cpuserial
