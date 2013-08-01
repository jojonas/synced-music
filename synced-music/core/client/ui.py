import sys
from PyQt4 import QtCore, QtGui
from ..util import log

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

		frmControls = QtGui.QGroupBox("Controls", self)
		layoutControls = QtGui.QHBoxLayout(frmControls)
		self.btnReset = QtGui.QPushButton("Reset", frmControls)
		self.btnResync = QtGui.QPushButton("Resync", frmControls)
		layoutControls.addWidget(self.btnReset)
		layoutControls.addWidget(self.btnResync)
		layoutLeftSide.addWidget(frmControls)
	
		self.txtMetrix = QtGui.QListWidget(self)
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
