import socket
import select
import threading
import random

from ..util import network as sharednet
from ..util import timer

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
		self.nextSendChunk = 0
		self.sendChunkInterval = 1.0

	def quit(self):
		self.quitFlag.set()

	def run(self):
		while not self.quitFlag.isSet():
			readable, writeable, error = select.select(self.readSocketList, [], [], 0)
			for sock in readable:
				if sock is self.serverSocket:
					clientSocket, address = sock.accept()
					self.readSocketList.append(clientSocket)
					self.logger.info("Client connected from " + str(address))
				else:
					data = sock.recv(1024)
					if data:
						self.logger.warning("Received data (this shouldn't happen...): " + data)

			currentTime = self.timer.time()
			
			# update timer from TIME TO TIME! HA!
			if self.nextTimerUpdate <= currentTime:
				self.timer.update()
				self.nextTimerUpdate = currentTime + random.random()

			# Send timestamp
			if self.nextSendTimestamp <= currentTime:
				packet = struct.pack("Bf", sharednet.TIMESTAMP_PACKET_ID, currentTime)

				for sock in self.readSocketList:
					if sock is not self.serverSocket:
						sock.send(packet)
					
				self.nextSendTimestamp = currentTime + self.sendTimestampInterval

			# Send chunk
			if self.nextSendChunk <= currentTime:
				self.nextSendChunk = self.sendChunkInterval