import threading

import pyaudio

from PyQt4 import QtCore

from ..util import audio as audio
from ..util import threads

CHUNKSIZE = 1024

class SoundDeviceReader(threads.QStoppableThread):
	def __init__(self, logger):
		threads.QStoppableThread.__init__(self, name="Server Audio")
		self.paHandler = pyaudio.PyAudio()

		self.stream = self.paHandler.open(format = audio.SAMPLE_FORMAT, channels = audio.CHANNELS, rate = audio.SAMPLE_RATE, input=True)
		self.streamLock = threading.Lock()

		self.readBuffer = ""
		self.readBufferLock = threading.Lock()

		self.logger = logger


	@QtCore.pyqtSlot(int)
	def openDevice(self, device):
		self.logger.info("Changing input device to %d.", device)
		with self.streamLock:
			self.stream.close()
			self.stream = self.paHandler.open(input_device_index=device, format = audio.SAMPLE_FORMAT, channels = audio.CHANNELS, rate = audio.SAMPLE_RATE, input=True)

	def run(self):
		while not self.done():
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

	def __del__(self):
		with self.streamLock:
			self.stream.stop_stream()
			self.stream.close()
			self.paHandler.terminate()

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