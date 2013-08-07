import threading

import pyaudio

from ..util import audio as audio

CHUNKSIZE = 1024

class SoundDeviceReader(threading.Thread):
	def __init__(self, logger):
		threading.Thread.__init__(self)
		self.paHandler = pyaudio.PyAudio()
		self.stream = self.paHandler.open(format = audio.SAMPLE_FORMAT, channels = audio.CHANNELS, rate = audio.SAMPLE_RATE, input=True)
		self.readBuffer = ""
		self.readBufferLock = threading.Lock()

		self.quitFlag = threading.Event()

		self.logger = logger

	def quit(self):
		self.stream.stop_stream()
		self.stream.close()
		self.paHandler.terminate()

		self.quitFlag.set()

	def run(self):
		while not self.quitFlag.isSet():
			try:
				data = self.stream.read(CHUNKSIZE)

				self.readBufferLock.acquire()
				self.readBuffer += data
				self.readBufferLock.release()
			except IOError as e:
				self.logger.error("Sound could not be read. Exception error following.")
				self.logger.exception(e)
			except Exception as e:
				self.logger.exception(e)

	def getBufferSize(self):
		self.readBufferLock.acquire()
		size = len(self.readBuffer)
		self.readBufferLock.release()
		return size

	def getBuffer(self, length):
		self.readBufferLock.acquire()
		size = len(self.readBuffer)
		if size < length:
			raise IOError("Not enough data to read in SoundDeviceReader.getBuffer - requested length: " + str(length))
		ret = self.readBuffer[:length]
		self.readBuffer = self.readBuffer[length:]
		self.readBufferLock.release()
		return ret

	