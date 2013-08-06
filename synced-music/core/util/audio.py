import pyaudio

# Mostly syned-music is written to be rather robust in the sense that server and client don't have to
# have many variables that should be set according to each other. Most of the configurable values are
# rather free to set on both sides with the other side mostly adapting to it. Including the port in network.py 
# this is also an exception.

# Sound constants
SAMPLE_FORMAT = pyaudio.paInt16
SAMPLE_RATE = 44100
