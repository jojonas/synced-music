import threading
import socket
import select

from ..util import network as sharednet
from ..util import timer 

class SyncedMusicClient(threading.Thread):
	def __init__(self, logger):
		threading.Thread.__init__(self)
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect(('localhost', sharednet.PORT))

		self.logger = logger
		self.quitFlag = threading.Event()
		self.timer = timer.HighPrecisionTimer()
		self.packetBuffer = "" # a buffer, because it's not gauaranteed that every single send corresponds to a single recv

	def quit(self):
		self.quitFlag.set()

	def run(self):
		while not self.quitFlag.isSet():
			readableSockets = select.select([self.socket], [], [], 0)[0]
			for sock in readableSockets:
				self.packetBuffer += sock.recv(4096)

			idSize = struct.calcsize("B")
			if len(self.packetBuffer) >= idSize:
				type = struct.unpack("B", self.packetBuffer[0])[0]
				if type == sharednet.TIMESTAMP_PACKET_ID:
					packetSize = struct.calcsize("Bf")
					if len(self.packetBuffer) >= packetSize:
						type, timestamp = struct.unpack("Bf", self.packetBuffer[0:packetSize])
						self.packetBuffer = self.packetBuffer[packetSize:]
						self.timer.update(timestamp)
				elif type == sharednet.CHUNK_PACKET_ID:
					pass
				else:
					self.logger.warning("Received unknown packet id: " + str(type))