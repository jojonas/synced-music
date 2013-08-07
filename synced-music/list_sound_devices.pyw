import pyaudio

paHandler = pyaudio.PyAudio()
deviceCount = paHandler.get_device_count()
print str(deviceCount) + " devices."
defaultIndex = paHandler.get_default_input_device_info()["index"]
for i in xrange(deviceCount):	
	suffix = ""
	deviceInfo = paHandler.get_device_info_by_index(i)
	
	if defaultIndex == deviceInfo["index"]:
		suffix = " (This is the default device)"
		
	print "Device #" + str(i) + ": " + deviceInfo["name"] + suffix