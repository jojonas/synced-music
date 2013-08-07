import pyaudio

# Mostly synced-music is written to be rather robust in the sense that server and client don't have to
# have many variables that should be set according to each other. Most of the configurable values are
# rather free to set on both sides with the other side mostly adapting to it. Including the port in network.py 
# this is also an exception.

# Sound constants
SAMPLE_FORMAT = pyaudio.paInt16
SAMPLE_RATE = 44100
CHANNELS = 2

def bytesToSeconds(bytes):
	return float(bytes)/CHANNELS/SAMPLE_RATE/pyaudio.get_sample_size(SAMPLE_FORMAT)

def secondsToBytes(seconds):
	# must be a multiple of CHANNELS*sample_size (for dropping/cropping. don't mess up the words)
	sample_size = pyaudio.get_sample_size(SAMPLE_FORMAT)
	exact_bytes = int(seconds*CHANNELS*SAMPLE_RATE*sample_size)
	return exact_bytes - exact_bytes % (CHANNELS*sample_size)
