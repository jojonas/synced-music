from PyQt4 import QtGui, QtCore
from collections import OrderedDict

class Metrix(QtGui.QTreeWidget):
	def __init__(self, parent=None, updateInterval=100):
		QtGui.QTreeWidget.__init__(self, parent)
		self.variables = OrderedDict()
		self.treeitems = {}

		self.setColumnCount(2)
		headerItem = QtGui.QTreeWidgetItem()
		headerItem.setData(0,0, "name")
		headerItem.setData(1,0, "value")
		self.setHeaderItem(headerItem)

		self.timer = QtCore.QTimer(self)
		self.timer.setInterval(updateInterval)
		self.timer.timerEvent = self.update
		self.timer.start()

	def add(self, name, callback):
		self.variables[name] = callback

		self.treeitems[name] = QtGui.QTreeWidgetItem()
		self.treeitems[name].setData(0, 0, name)
		self.treeitems[name].setData(1, 0, repr(callback()))

		self.addTopLevelItem(self.treeitems[name])

	def remove(self, name):
		self.variables.remove(name)
		self.removeItemWidget(self.treeitems[name])
		del self.treeitems[name]

	def update(self, dummy=None):
		for name, callback in self.variables.iteritems():
			self.treeitems[name].setData(1, 0, repr(callback()))

def getLogger():
	return logging.getLogger(__name__)