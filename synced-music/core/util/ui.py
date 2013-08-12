from PyQt4 import QtCore, QtGui
from ..util import log, metrix

class SecondsWidget(QtGui.QWidget):
	def __init__(self, title, range, step=1.0):
		QtGui.QWidget.__init__(self)
		layout = QtGui.QHBoxLayout(self)
		layout.setMargin(1)
		label = QtGui.QLabel(title, self)
		label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		layout.addWidget(label)
		self.spinner = QtGui.QDoubleSpinBox(self)
		self.spinner.setSuffix(" s")
		self.spinner.setDecimals(2)
		self.spinner.setRange(range[0], range[1])
		self.spinner.setSingleStep(step)
		label.setBuddy(self.spinner)
		layout.addWidget(self.spinner)

		self.setValue = self.spinner.setValue
		self.valueChanged = self.spinner.valueChanged

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
