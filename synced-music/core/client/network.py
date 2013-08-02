import threading
import socket
import select
import struct

from ..util import network as sharednet
from ..util import timer, log

class SyncedMusicClient(threading.Thread):
	def __init__(self, logger):
		threading.Thread.__init__(self)
		self.socket = None
		self.logger = logger
		self.quitFlag = threading.Event()
		self.timer = timer.HighPrecisionTimer()
		self.packetBuffer = "" # a buffer, because it's not gauaranteed that every single send corresponds to a single recv

	def connect(self, host):
		self.packetBuffer = ""
		self.timer.reset()
		if self.socket is not None:
			self.socket.close()
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((host, sharednet.PORT))
		self.logger.info("connected to %s" % host)

	def quit(self):
		self.quitFlag.set()
		if self.socket is not None:
			self.socket.close()

	def run(self):
		while not self.quitFlag.isSet():
			try:
				if self.socket is None:
					continue
				readableSockets = select.select([self.socket], [], [], 0)[0]
				for sock in readableSockets:
					chunk = sock.recv(4096)
					self.logger.debug("chunk: %s", str(struct.unpack("Bd", chunk)))
					self.packetBuffer += chunk
				idSize = struct.calcsize("B")
				if len(self.packetBuffer) >= idSize:
					type = struct.unpack("B", self.packetBuffer[0])[0]
					if type == sharednet.TIMESTAMP_PACKET_ID:
						packetSize = struct.calcsize("Bd")
						if len(self.packetBuffer) >= packetSize:
							type, timestamp = struct.unpack("Bd", self.packetBuffer[0:packetSize])
							self.packetBuffer = self.packetBuffer[packetSize:]
							self.timer.update(timestamp)
					elif type == sharednet.CHUNK_PACKET_ID:
						pass
					else:
						self.logger.warning("Received unknown packet id: " + str(type))
			except KeyboardInterrupt:
				break
			except Exception as e:
				self.logger.exception(e)
