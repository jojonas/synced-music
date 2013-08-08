import threading

from PyQt4 import QtCore

class PyStoppableThread(threading.Thread):
	def __init__(self, name=None):
		threading.Thread.__init__(self, name=name)
		self._stopFlag = threading.Event()

	def stop(self):
		self._stopFlag.set()
		if threading.currentThread() is self:
			raise RuntimeError("StoppableThread.stop() must not be called by the thread itself.")
		else:
			self.join()

	def done(self):
		return self._stopFlag.isSet()

	def waitStop(self, maxTime=None):
		return self._stopFlag.wait(maxTime)

class QStoppableThread(QtCore.QThread):
	def __init__(self, name=None):
		QtCore.QThread.__init__(self)
		self.name = name
		self._stopFlag = threading.Event()

	@QtCore.pyqtSlot()
	def stop(self):
		self._stopFlag.set()

	def done(self):
		return self._stopFlag.isSet()

	def waitStop(self, maxTime=None):
		return self._stopFlag.wait(maxTime)

	def __del__(self):
		self.wait()

