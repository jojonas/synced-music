import threading
import socket
import select
import struct

import wave

from ..util import network as sharednet
from ..util import timer, log, threads

import audio

class SyncedMusicClient(threads.StoppableThread):
	def __init__(self, logger):
		threads.StoppableThread.__init__(self, name="Client Network")
		self.logger = logger

		self.socket = None
		self.socketLock = threading.Lock()
		self.connectedFlag = threading.Event()
		
		self.timer = timer.HighPrecisionTimer()
		self.soundWriter = audio.SoundDeviceWriter(logger, self.timer) 

		self.packetBuffer = "" # a buffer, because it's not gauaranteed that every single send corresponds to a single recv

	def connect(self, host):
		self.packetBuffer = ""
		self.timer.reset()
		with self.socketLock:
			self.connectedFlag.clear()
			try:
				if self.socket is not None:
					self.socket.close()
				self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.socket.connect((host, sharednet.PORT))
				self.socket.settimeout(15)
				self.connectedFlag.set()
				self.logger.info("connected to %s" % host)
			except Exception as e:
				self.logger.exception(e)
				self.socket = None

	def teardown(self):
		with self.socketLock:
			if self.socket is not None:
				self.socket.close()

	def run(self):
		self.soundWriter.start()

		idSize = struct.calcsize("B")
		while not self.done():
			try:
				self.connectedFlag.wait(0.3)
				with self.socketLock:
					if self.socket is None:
						continue
					#readableSockets = select.select([self.socket], [], [], 0)[0]
					#for sock in readableSockets:
					#	chunk = sock.recv(4096)
					#	self.packetBuffer += chunk

					# Try blocking version
					chunk = self.socket.recv(4096)
					self.packetBuffer += chunk

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
				break
			except Exception as e:
				self.logger.exception(e)

		self.soundWriter.quit()
