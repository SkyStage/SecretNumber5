from dronekit import connect

#Connet to UDP endpoint
vehicle = connect('127.0.0.1:14550',wait_ready = True)
while True:
	print "location %s" % vehicle.location.local_frame.north
	print"attitude %s" % vehicle.attitude
