from PyQt4 import QtGui
from collections import OrderedDict

class Metrix(QtGui.QTreeWidget):
	def __init__(self, parent=None):
		QtGui.QTreeWidget.__init__(self, parent)
		self.variables = OrderedDict()
		self.treeitems = {}

		self.setColumnCount(2)
		headerItem = QtGui.QTreeWidgetItem()
		headerItem.setData(0,0, "name")
		headerItem.setData(1,0, "value")
		self.setHeaderItem(headerItem)

	def add(self, name, callback):
		self.variables[name] = callback

		self.treeitems[name] = QtGui.QTreeWidgetItem()
		self.treeitems[name].setData(0, 0, name)
		self.treeitems[name].setData(1, 0, str(callback()))

		self.addTopLevelItem(self.treeitems[name])

	def remove(self, name):
		self.variables.remove(name)
		self.removeItemWidget(self.treeitems[name])
		del self.treeitems[name]

	def update(self):
		for name, callback in self.variables.iteritems():
			self.treeitems[name].setData(1, 0, str(callback()))

def getLogger():
	return logging.getLogger(__name__)