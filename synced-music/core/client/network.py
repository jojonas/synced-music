import threading
import socket
import select
import struct
import zlib
import time

import wave

from ..util import network as sharednet
from ..util import timer, log, threads

import audio

from PyQt4 import QtCore

class SyncedMusicClient(threads.QStoppableThread):
	def __init__(self, logger):
		threads.QStoppableThread.__init__(self, name="Client Network")
		self.logger = logger

		self.socket = None
		self.socketLock = threading.Lock()
		self.connectedFlag = threading.Event()
		
		self.timer = timer.HighPrecisionTimer()
		self.soundWriter = audio.SoundDeviceWriter(logger, self.timer) 
		self.started.connect(self.soundWriter.start)
		self.finished.connect(self.soundWriter.stop)

		self.packetBuffer = "" # a buffer, because it's not gauaranteed that every single send corresponds to a single recv
		self.playbackOffset = 0 #s
		self.remoteHost = ""
		
		self.reconnectInterval = 2.0

	@QtCore.pyqtSlot(QtCore.QString)
	def connect(self, host):
		self.packetBuffer = ""
		self.timer.reset()
		with self.socketLock:
			success = False
			self.connectedFlag.clear()
			try:
				if self.socket is not None:
					self.socket.close()
				self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.socket.settimeout(15.0)
				self.socket.connect((host, sharednet.PORT))
				self.remoteHost = host
				self.connectedFlag.set()
				self.logger.info("Connected to %s" % host)
				success = True
			except Exception as e:
				self.logger.exception(e)
				self.socket = None
		return success
		
	@QtCore.pyqtSlot(int)
	def setPlaybackOffset(self, value):
		self.logger.info("Playback offset changed to %.3f s.", value)
		self.playbackOffset = value

	def run(self):
		idSize = struct.calcsize("!B")
		while not self.done():
			try:
				self.connectedFlag.wait(0.3)
				try:
					with self.socketLock:
						if self.socket is None:
							continue

						# Try blocking version
						
						chunk = self.socket.recv(4096)
						if len(chunk) == 0:
							raise socket.error("recv returned 0 bytes")
						self.packetBuffer += chunk
						
				except socket.error:
					self.logger.error("Connection lost. Attempting to reconnect.")
					self.connectedFlag.clear()
					while (not self.connectedFlag.isSet()) and (not self.connect(self.remoteHost)): # warning: race condition may occur here
						self.logger.info("Attempting again in %.2f seconds.", self.reconnectInterval)
						self.waitStop(self.reconnectInterval)
				
				if len(self.packetBuffer) >= idSize:
					type = struct.unpack("!B", self.packetBuffer[0])[0]
					if type == sharednet.TIMESTAMP_PACKET_ID:
						packetSize = struct.calcsize("!Bd")
						if len(self.packetBuffer) >= packetSize:
							self.logger.debug("Timestamp received")
							type, timestamp = struct.unpack("!Bd", self.packetBuffer[0:packetSize])
							self.packetBuffer = self.packetBuffer[packetSize:]
							self.timer.update(timestamp)
					elif type == sharednet.CHUNK_PACKET_ID:
						headerSize = struct.calcsize("!BdI")
						if len(self.packetBuffer) >= headerSize:
							type, playAt, bufferSize = struct.unpack("!BdI", self.packetBuffer[0:headerSize])
							if len(self.packetBuffer) >= headerSize + bufferSize:
								self.logger.debug("Chunk received")
								soundBuffer = self.packetBuffer[headerSize:headerSize+bufferSize]
								soundBuffer = zlib.decompress(soundBuffer) # COMPRESSION!
								self.packetBuffer = self.packetBuffer[headerSize+bufferSize:]
								self.soundWriter.enqueueSound(playAt + self.playbackOffset, soundBuffer)
						pass
					else:
						self.logger.critical("Received unknown packet id: " + str(type))
			except KeyboardInterrupt:
				break
			except Exception as e:
				self.logger.exception(e)

	def __del__(self):
		with self.socketLock:
			if self.socket is not None:
				self.socket.close()
