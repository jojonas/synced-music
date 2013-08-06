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
		self.nextSendChunk = 0
		self.sendChunkInterval = 1.0

		self.soundReader = audio.SoundDeviceReader(logger)
		self.bufferRead = False

	def quit(self):
		self.soundReader.quit()
		self.quitFlag.set()

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

					for sock in self.readSocketList:
						if sock is not self.serverSocket:
							print "SENDING:",log.hex(packet), currentTime
							sock.send(packet)
					
					self.nextSendTimestamp = currentTime + self.sendTimestampInterval

				# Send chunk
				if self.nextSendChunk <= currentTime:
					self.nextSendChunk = currentTime + self.sendChunkInterval

				#self.logger.debug("Sound buffer data length: " + str(self.soundReader.getBufferSize()))
				readSize = 2*2*44100
				if self.soundReader.getBufferSize() >= readSize and not self.bufferRead:
					self.bufferRead = True
					data = self.soundReader.getBufferData(0, readSize)
					self.soundReader.dropBufferFront(readSize)

					self.logger.error("len: " + str(len(data)))

					transformed = struct.unpack("="+str(readSize/2)+"h", data)

					self.logger.error("size: " + str(len(transformed)))
					f = open("waveformoutput.plot", "w")
					i = 0
					#self.logger.error("data: " + str(data))
					for val in transformed:
						f.write(str(i) + "\t" + str(val) + "\n")
						i += 1
					f.close()

					wavFile = wave.open("out.wav", "w")
					wavFile.setparams((2, 2, 44100, readSize, "NONE", "not compressed"))
					wavFile.writeframes(data)
					wavFile.close()
			except KeyboardInterrupt:
				self.soundReader.quit()
				break
			except Exception as e:
				self.logger.exception(e)
				