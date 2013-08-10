import sys
from PyQt4 import QtCore, QtGui
from ..util import log, metrix, ui
import pyaudio

class Widget(ui.Widget):
	def setup(self):
		frmControls = QtGui.QGroupBox("Controls", self)
		layoutControls = QtGui.QHBoxLayout(frmControls)
		self.btnResync = QtGui.QPushButton("&Resync", frmControls)
		lblDevice = QtGui.QLabel("&Sound device:", frmControls)
		self.cmbDevice = QtGui.QComboBox(frmControls)
		lblDevice.setBuddy(self.cmbDevice)
		
		layoutControls.addWidget(self.btnResync)
		layoutControls.addWidget(lblDevice)
		layoutControls.addWidget(self.cmbDevice)

		self.addLeftSide(frmControls)
	
		paHandler = pyaudio.PyAudio()
		for i in xrange(paHandler.get_device_count()):
			deviceInfo = paHandler.get_device_info_by_index(i)
			self.logger.info("Devices: %s", str(deviceInfo))
			self.cmbDevice.addItem(deviceInfo["name"])
		self.cmbDevice.setCurrentIndex(paHandler.get_default_input_device_info()["index"])
		paHandler.terminate()

		self.setWindowTitle("Server - SyncedMusic")
