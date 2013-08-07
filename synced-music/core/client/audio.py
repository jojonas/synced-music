import threading
import wave
import Queue

import pyaudio

from ..util import audio as audio

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

class SoundDeviceWriter(threading.Thread):
	def __init__(self, logger, timer):
		threading.Thread.__init__(self)
		self.paHandler = pyaudio.PyAudio()
		self.stream = self.paHandler.open(format = audio.SAMPLE_FORMAT, channels = audio.CHANNELS, rate = audio.SAMPLE_RATE, output=True)
		self.soundBufferQueue = Queue.Queue(-1) # infinite size

		self.quitFlag = threading.Event()
		self.logger = logger
		self.timer = timer

	def quit(self):
		self.stream.stop_stream()
		self.stream.close()
		self.paHandler.terminate()
		self.quitFlag.set()

	def run(self):
		while not self.quitFlag.isSet():
			try:
				playAt, soundBuffer = self.soundBufferQueue.get(block=False)
				deltaTime = playAt - self.timer.time()
				if deltaTime > 0:
					# Sleep, but don't "oversleep" a quit event. wait() returns the quitFlag-state, which is then checked.
					quitSet = self.quitFlag.wait(deltaTime)
					if quitSet:
						break
				else: # deltaTime <= 0
					# chop off samples that should have been played in the past
					soundBuffer = soundBuffer[int(audio.secondsToBytes(deltaTime)):]
				self.stream.write(soundBuffer)
			except IOError as e:
				self.logger.error("Sound could not be played. Exception error following.")
				self.logger.exception(e)
			except Queue.Empty as e:
				#self.logger.warning("Sound buffer queue empty.")
				pass
			except Exception as e:
				self.logger.exception(e)

	def enqueueSound(self, playAt, buffer):
		self.soundBufferQueue.put((playAt, buffer))
