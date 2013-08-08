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

	def stop(self):
		self.waveFile.close()

	def start(self):
		pass
		
	def getEnqueued(self):
		return 0

	def enqueueSound(self, playAt, buffer):
		self.waveFile.writeframes(buffer)
		pass

class SoundDeviceWriter(threads.QStoppableThread):
	def __init__(self, logger, timer):
		threads.QStoppableThread.__init__(self, name="Client Audio")
		self.paHandler = pyaudio.PyAudio()

		self.stream = self.paHandler.open(format = audio.SAMPLE_FORMAT, channels = audio.CHANNELS, rate = audio.SAMPLE_RATE, output=True)
		
		self.soundBufferQueue = Queue.Queue(-1) # infinite size

		self.logger = logger
		self.timer = timer

	def run(self):
		while not self.done():
			try:
				playAt, soundBuffer = self.soundBufferQueue.get(block=True, timeout=5.0)
				deltaTime = playAt - self.timer.time()

				if deltaTime > 0:
					if deltaTime > 10.0:
						continue
					else:
						self.logger.debug("Waiting for %f seconds.", deltaTime)
						# Sleep, but don't "oversleep" a quit event. waitStop() sleeps at most deltaTime seconds and returns whether the thread will quit afterwards
						sleepUntil = self.timer.time() + deltaTime
						waitStopTime = deltaTime - 0.05
						if waitStopTime > 0:
							if self.waitStop(waitStopTime):
								break
						while self.timer.time() < sleepUntil:
							pass

				else: # deltaTime <= 0
					# chop off samples that should have been played in the past
					
					cropBytes = audio.secondsToBytes(-deltaTime)
					self.logger.debug("Cropping %f seconds = %d bytes.", -deltaTime, cropBytes)
					soundBuffer = soundBuffer[cropBytes:]

				if self.stream != None:
					self.stream.write(soundBuffer, exception_on_underflow=False)

			except IOError as e:
				self.logger.error("Sound could not be played. Exception error following.")
				self.logger.exception(e)
			except Queue.Empty:
				self.logger.warning("Sound buffer queue empty.")
				pass
			except Exception as e:
				self.logger.exception(e)

	def __del__(self):
		self.stream.stop_stream()
		self.stream.close()
		self.paHandler.terminate()
		self.stream = None

	def enqueueSound(self, playAt, buffer):
		self.soundBufferQueue.put((playAt, buffer))
		
	def getEnqueued(self):
		return self.soundBufferQueue.qsize()
