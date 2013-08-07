import sys
from PyQt4 import QtCore, QtGui
from ..util import log, metrix
import pyaudio

class Widget(QtGui.QWidget):
	def __init__(self, logger):
		QtGui.QWidget.__init__(self)
		self.logger = logger
		self.resize(250,150)
		self.setWindowTitle("Server - SyncedMusic")
		self.createWidgets()
		self.show()
		
	def createWidgets(self):
		layoutMain = QtGui.QHBoxLayout(self)
		layoutLeftSide = QtGui.QVBoxLayout(self)

		frmControls = QtGui.QGroupBox("Controls", self)
		layoutControls = QtGui.QHBoxLayout(frmControls)
		self.btnResync = QtGui.QPushButton("&Resync", frmControls)
		lblDevice = QtGui.QLabel("&Sound device:", frmControls)
		self.cmbDevice = QtGui.QComboBox(frmControls)
		lblDevice.setBuddy(self.cmbDevice)
		
		layoutControls.addWidget(self.btnResync)
		layoutControls.addWidget(lblDevice)
		layoutControls.addWidget(self.cmbDevice)
		layoutLeftSide.addWidget(frmControls)
	
		self.txtMetrix = metrix.Metrix(self)
		layoutLeftSide.addWidget(self.txtMetrix)
		layoutMain.addLayout(layoutLeftSide)
		self.metrix = self.txtMetrix

		self.lstLog = log.TextLog(self)
		layoutMain.addWidget(self.lstLog)

		paHandler = pyaudio.PyAudio()
		for i in xrange(paHandler.get_device_count()):
			deviceInfo = paHandler.get_device_info_by_index(i)
			self.logger.info("Devices: %s", str(deviceInfo))
			self.cmbDevice.addItem(deviceInfo["name"])
		self.cmbDevice.setCurrentIndex(paHandler.get_default_input_device_info()["index"])
		paHandler.terminate()


