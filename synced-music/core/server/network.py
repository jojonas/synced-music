import socket
import select
import threading
import random
import struct
import time
import zlib

from ..util import network as sharednet
from ..util import timer, log, threads

import audio

class SyncedMusicServer(threads.StoppableThread):
	def __init__(self, logger):
		threads.StoppableThread.__init__(self, name="Server Network")
		self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.serverSocket.bind(('', sharednet.PORT))
		self.serverSocket.listen(4)
		
		self.readSocketList = [self.serverSocket]
		self.logger = logger
		self.timer = timer.HighPrecisionTimer()

		self.nextTimerUpdate = 0
		self.nextSendTimestamp = 0
		self.sendTimestampInterval = 0.8
		self.sendChunkInterval = 0.5
		self.playChunkDelay = 3.0

		self.soundReader = audio.SoundDeviceReader(logger)

	def sendToAll(self, packet):
		for sock in self.readSocketList:
			if sock is not self.serverSocket:
				sock.send(packet)

	def run(self):
		self.soundReader.start()
		
		chunkLengthBytes = audio.audio.secondsToBytes(self.sendChunkInterval)

		while not self.done():
			try:
				readable, writeable, error = select.select(self.readSocketList, [], [], 0)
				for sock in readable:
					if sock is self.serverSocket:
						clientSocket, address = sock.accept()
						self.readSocketList.append(clientSocket)
						self.logger.info("Client connected from %s.", address)
					else:
						try:
							data = sock.recv(1024)
							if data:
								self.logger.warning("Received data (this shouldn't happen...): %s.", data)
						except socket.error as e:
							self.logger.exception(e)
							self.logger.info("Closing socket %s.", socket)
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
				if self.soundReader.getBufferSize() >= chunkLengthBytes:
					readBytes = self.soundReader.getBuffer(chunkLengthBytes)
					self.logger.debug("Sending chunk.")
					assert len(readBytes) == chunkLengthBytes
					readBytes = zlib.compress(readBytes, 1) # COMPRESSION! (saves about 40% bandwidth, even on level=1 of 9)
					packet = struct.pack("BdI", sharednet.CHUNK_PACKET_ID, currentTime + self.playChunkDelay, len(readBytes))
					packet += readBytes
					self.sendToAll(packet)

				# Sleeping optimization
				sleepTime = min([
					 self.nextTimerUpdate - currentTime, 
					 self.nextSendTimestamp - currentTime, 
					 audio.audio.bytesToSeconds(chunkLengthBytes - self.soundReader.getBufferSize())
				]) - 0.1
				
				if sleepTime > 0:
					#self.logger.debug("Will sleep %f seconds.", sleepTime)
					time.sleep(sleepTime)

			except KeyboardInterrupt:
				self.stop()
			except Exception as e:
				self.logger.exception(e)

		self.soundReader.stop()