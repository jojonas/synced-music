import socket
import select
import threading
import random
import struct
import wave

from ..util import network as sharednet
from ..util import timer, log

import audio

class SyncedMusicServer(threading.Thread):
	def __init__(self, logger):
		threading.Thread.__init__(self)
		self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.serverSocket.bind(('', sharednet.PORT))
		self.serverSocket.listen(4)
		
		self.quitFlag = threading.Event()
		self.readSocketList = [self.serverSocket]
		self.logger = logger
		self.timer = timer.HighPrecisionTimer()

		self.nextTimerUpdate = 0
		self.nextSendTimestamp = 0
		self.sendTimestampInterval = 0.8
		self.sendChunkInterval = 1.0
		self.playChunkDelay = 1.0

		self.soundReader = audio.SoundDeviceReader(logger)

	def quit(self):
		self.soundReader.quit()
		self.quitFlag.set()

	def sendToAll(self, packet):
		for sock in self.readSocketList:
			if sock is not self.serverSocket:
				sock.send(packet)

	def run(self):
		self.soundReader.start()

		while not self.quitFlag.isSet():
			try:
				readable, writeable, error = select.select(self.readSocketList, [], [], 0)
				for sock in readable:
					if sock is self.serverSocket:
						clientSocket, address = sock.accept()
						self.readSocketList.append(clientSocket)
						self.logger.info("client connected from %s", address)
					else:
						try:
							data = sock.recv(1024)
							if data:
								self.logger.warning("received data (this shouldn't happen...): %s", data)
						except socket.error as e:
							self.logger.exception(e)
							self.logger.info("closing socket %s", socket)
							sock.close()
							self.readSocketList.remove(sock)

				currentTime = self.timer.time()
			
				# update timer from TIME TO TIME! HA!
				if self.nextTimerUpdate <= currentTime:
					self.timer.update()
					self.nextTimerUpdate = currentTime + random.random()

				# Send timestamp
				if self.nextSendTimestamp <= currentTime:
					#self.logger.info("sending timestamp %f", currentTime)
					packet = struct.pack("Bd", sharednet.TIMESTAMP_PACKET_ID, currentTime)
					self.sendToAll(packet)
					self.nextSendTimestamp = currentTime + self.sendTimestampInterval

				# Send chunk
				chunkLengthBytes = audio.audio.secondsToBytes(self.sendChunkInterval)
				if self.soundReader.getBufferSize() >= chunkLengthBytes:
					readBytes = self.soundReader.getBuffer(chunkLengthBytes)
					self.logger.info("Sending chunk.")
					# hopefully len(readBytes) == chunkLengthBytes
					packet = struct.pack("BdI", sharednet.CHUNK_PACKET_ID, currentTime + self.playChunkDelay, len(readBytes))
					packet += readBytes
					self.sendToAll(packet)

			except KeyboardInterrupt:
				self.quit()
			except Exception as e:
				self.logger.exception(e)
				