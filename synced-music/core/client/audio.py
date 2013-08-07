import threading
import wave
import Queue

import pyaudio

from ..util import audio as audio
from ..util import threads

class WaveFileWriter(object):
	def __init__(self, logger, timer):
		self.waveFile = wave.open("outwave.wav", "w")
		self.waveFile.setnchannels(audio.CHANNELS)
		self.waveFile.setsampwidth(audio.pyaudio.get_sample_size(audio.SAMPLE_FORMAT))
		self.waveFile.setframerate(audio.SAMPLE_RATE)

	def quit(self):
		self.waveFile.close()

	def start(self):
		pass

	def enqueueSound(self, playAt, buffer):
		self.waveFile.writeframes(buffer)
		pass

class SoundDeviceWriter(threads.StoppableThread):
	def __init__(self, logger, timer):
		threads.StoppableThread.__init__(self, name="Client Audio")
		self.paHandler = pyaudio.PyAudio()

		self.stream = self.paHandler.open(format = audio.SAMPLE_FORMAT, channels = audio.CHANNELS, rate = audio.SAMPLE_RATE, output=True)
		self.streamLock = threading.Lock()

		self.soundBufferQueue = Queue.Queue(-1) # infinite size

		self.logger = logger
		self.timer = timer

	def teardown(self):
		with self.streamLock:
			self.stream.stop_stream()
			self.stream.close()
			self.paHandler.terminate()
			self.stream = None

	def run(self):
		while not self.done():
			try:
				playAt, soundBuffer = self.soundBufferQueue.get(block=True, timeout=5)
				deltaTime = playAt - self.timer.time()

				if deltaTime > 0:
					# Sleep, but don't "oversleep" a quit event. waitQuit() sleeps at most deltaTime seconds and returns whether the thread will quit afterwards
					if self.waitQuit(deltaTime):
						break
				else: # deltaTime <= 0
					# chop off samples that should have been played in the past
					soundBuffer = soundBuffer[int(audio.secondsToBytes(deltaTime)):]

				with self.streamLock:
					if self.stream != None:
						self.stream.write(soundBuffer)

			except IOError as e:
				self.logger.error("Sound could not be played. Exception error following.")
				self.logger.exception(e)
			except Queue.Empty:
				self.logger.warning("Sound buffer queue empty.")
				pass
			except Exception as e:
				self.logger.exception(e)

	def enqueueSound(self, playAt, buffer):
		self.soundBufferQueue.put((playAt, buffer))
