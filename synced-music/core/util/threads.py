import threading

class StoppableThread(threading.Thread):
	def __init__(self, name=None):
		threading.Thread.__init__(self, name=name)
		self._quitFlag = threading.Event()

	def quit(self):
		self._quitFlag.set()
		self.join()
		self.teardown()

	def teardown(self):
		pass

	def done(self):
		return self._quitFlag.isSet()

	def waitQuit(self, maxTime=None):
		return self._quitFlag.wait(maxTime)