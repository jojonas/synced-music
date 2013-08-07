import threading
import socket
import select
import struct

import wave

from ..util import network as sharednet
from ..util import timer, log

import audio

class SyncedMusicClient(threading.Thread):
	def __init__(self, logger):
		threading.Thread.__init__(self)
		self.socket = None
		self.logger = logger
		self.quitFlag = threading.Event()
		self.timer = timer.HighPrecisionTimer()
		self.packetBuffer = "" # a buffer, because it's not gauaranteed that every single send corresponds to a single recv
		self.socketLock = threading.Lock()
		self.soundWriter = audio.SoundDeviceWriter(logger, self.timer) #audio.WaveFileWriter(logger, self.timer)

	def connect(self, host):
		self.packetBuffer = ""
		self.timer.reset()
		with self.socketLock:
			try:
				if self.socket is not None:
					self.socket.close()
				self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.socket.connect((host, sharednet.PORT))
				self.logger.info("connected to %s" % host)
			except Exception as e:
				self.logger.exception(e)

	def quit(self):
		self.quitFlag.set()
		if self.socket is not None:
			self.socket.close()

	def run(self):
		self.soundWriter.start()
		while not self.quitFlag.isSet():
			try:
				if self.socket is None:
					continue
				with self.socketLock:
					readableSockets = select.select([self.socket], [], [], 0)[0]
					for sock in readableSockets:
						chunk = sock.recv(4096)
						self.packetBuffer += chunk
				idSize = struct.calcsize("B")
				if len(self.packetBuffer) >= idSize:
					type = struct.unpack("B", self.packetBuffer[0])[0]
					if type == sharednet.TIMESTAMP_PACKET_ID:
						packetSize = struct.calcsize("Bd")
						if len(self.packetBuffer) >= packetSize:
							self.logger.info("Timestamp packet")
							type, timestamp = struct.unpack("Bd", self.packetBuffer[0:packetSize])
							self.packetBuffer = self.packetBuffer[packetSize:]
							self.timer.update(timestamp)
					elif type == sharednet.CHUNK_PACKET_ID:
						headerSize = struct.calcsize("BdI")
						if len(self.packetBuffer) >= headerSize:
							type, playAt, bufferSize = struct.unpack("BdI", self.packetBuffer[0:headerSize])
							if len(self.packetBuffer) >= headerSize + bufferSize:
								self.logger.debug("Chunk received")
								soundBuffer = self.packetBuffer[headerSize:headerSize+bufferSize]
								self.packetBuffer = self.packetBuffer[headerSize+bufferSize:]
								self.soundWriter.enqueueSound(playAt, soundBuffer)
						pass
					else:
						self.logger.critical("Received unknown packet id: " + str(type))
			except KeyboardInterrupt:
				self.quit()
			except Exception as e:
				self.logger.exception(e)
		self.soundWriter.quit()