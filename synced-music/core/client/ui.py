import sys
from PyQt4 import QtCore, QtGui
from ..util import log, metrix

class Widget(QtGui.QWidget):
	def __init__(self):
		QtGui.QWidget.__init__(self)
		self.logger = log.getLogger()
		self.resize(250,150)
		self.setWindowTitle("Client")
		self.createWidgets()
		self.show()
		
	def createWidgets(self):
		layoutMain = QtGui.QHBoxLayout(self)
		layoutLeftSide = QtGui.QVBoxLayout(self)

		frmServerSelection = QtGui.QGroupBox("Server Selection", self)
		layoutServerSelection = QtGui.QHBoxLayout(frmServerSelection)
		lblServer = QtGui.QLabel("&server / host name:", frmServerSelection)
		self.txtServer = QtGui.QLineEdit(frmServerSelection)
		self.txtServer.setInputMask("000.000.000.000")
		lblServer.setBuddy(self.txtServer)
		layoutServerSelection.addWidget(lblServer)
		layoutServerSelection.addWidget(self.txtServer)
		
		layoutLeftSide.addWidget(frmServerSelection)

		frmControls = QtGui.QGroupBox("Controls", self)
		layoutControls = QtGui.QHBoxLayout(frmControls)
		self.btnReset = QtGui.QPushButton("Reset", frmControls)
		self.btnResync = QtGui.QPushButton("&Resync", frmControls)
		lblOffset = QtGui.QLabel("&offset (ms):", frmControls)
		self.spnOffset = QtGui.QSpinBox(frmControls)
		lblOffset.setBuddy(self.spnOffset)
		
		layoutControls.addWidget(self.btnReset)
		layoutControls.addWidget(self.btnResync)
		layoutControls.addWidget(lblOffset)
		layoutControls.addWidget(self.spnOffset)
		layoutLeftSide.addWidget(frmControls)
	
		self.txtMetrix = metrix.Metrix(self)
		self.txtMetrix.add("Name", lambda: self.__class__.__name__)
		layoutLeftSide.addWidget(self.txtMetrix)
		layoutMain.addLayout(layoutLeftSide)

		self.lstLog = log.TextLog(self)
		layoutMain.addWidget(self.lstLog)

		self.btnReset.clicked.connect(self.testLog)

	def testLog(self):
		self.logger.warning("HELLO?")

def show():
	app = QtGui.QApplication(sys.argv)
	widget = Widget()
	sys.exit(app.exec_())

if __name__=="__main__":
	show()
