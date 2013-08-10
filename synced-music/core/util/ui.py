from PyQt4 import QtCore, QtGui
from ..util import log, metrix

class Widget(QtGui.QWidget):
	def __init__(self, logger):
		QtGui.QWidget.__init__(self)
		self.logger = logger
		self.splitterLeftSide = QtGui.QSplitter(QtCore.Qt.Vertical, self)
		self._setup()
		self.setup()
		self.show()

	def addLeftSide(self, qwidget):
		#qwidget.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)
		self.splitterLeftSide.insertWidget(self.splitterLeftSide.count() - 1, qwidget)

	def setup(self):
		pass

	def _setup(self):
		layoutMain = QtGui.QHBoxLayout(self)
		splitterMain = QtGui.QSplitter(QtCore.Qt.Horizontal)
	
		self.txtMetrix = metrix.Metrix(self)
		self.splitterLeftSide.addWidget(self.txtMetrix)
		self.metrix = self.txtMetrix

		splitterMain.addWidget(self.splitterLeftSide)

		self.lstLog = log.TextLog(self)
		#self.lstLog.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
		splitterMain.addWidget(self.lstLog)

		splitterMain.setStretchFactor(1,10)
		self.splitterLeftSide.setStretchFactor(0, 10)

		layoutMain.addWidget(splitterMain)
