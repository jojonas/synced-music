import threading

import pyaudio

from ..util import audio as audio

CHUNKSIZE = 1024

class SoundDeviceReader(threading.Thread):
	def __init__(self, logger):
		threading.Thread.__init__(self)
		self.paHandler = pyaudio.PyAudio()

		self.stream = self.paHandler.open(format = audio.SAMPLE_FORMAT, channels = audio.CHANNELS, rate = audio.SAMPLE_RATE, input=True)
		self.streamLock = threading.Lock()

		self.readBuffer = ""
		self.readBufferLock = threading.Lock()

		self.quitFlag = threading.Event()

		self.logger = logger

	def openDevice(self, device):
		self.logger.info("Changing input device to %d.", device)
		with self.streamLock:
			self.stream.close()
			self.stream = self.paHandler.open(input_device_index=device, format = audio.SAMPLE_FORMAT, channels = audio.CHANNELS, rate = audio.SAMPLE_RATE, input=True)
		

	def quit(self):
		self.quitFlag.set()

		with self.streamLock:
			self.stream.stop_stream()
			self.stream.close()
			self.paHandler.terminate()

	def run(self):
		while not self.quitFlag.isSet():
			try:
				with self.streamLock:
					data = self.stream.read(CHUNKSIZE)

				with self.readBufferLock:
					self.readBuffer += data
			except IOError as e:
				self.logger.error("Sound could not be read. Exception error following.")
				self.logger.exception(e)
			except Exception as e:
				self.logger.exception(e)

	def getBufferSize(self):
		with self.readBufferLock:
			size = len(self.readBuffer)
		return size

	def getBuffer(self, length):
		with self.readBufferLock:
			size = len(self.readBuffer)
			if size < length:
				raise IOError("Not enough data to read in SoundDeviceReader.getBuffer - requested length: " + str(length))
			ret = self.readBuffer[:length]
			self.readBuffer = self.readBuffer[length:]
		return ret