import threading

class StoppableThread(threading.Thread):
	def __init__(self, name=None):
		threading.Thread.__init__(self, name=name)
		self._stopFlag = threading.Event()

	def stop(self):
		self._stopFlag.set()
		if threading.currentThread() is self:
			raise RuntimeError("StoppableThread.stop() is not meant to be called by the thread itself.")
		else:
			self.join()

	def done(self):
		return self._stopFlag.isSet()

	def waitStop(self, maxTime=None):
		return self._stopFlag.wait(maxTime)