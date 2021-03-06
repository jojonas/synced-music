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
		lblDevice.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
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

		frmSettings = QtGui.QGroupBox("Settings", self)
		layoutSettings = QtGui.QVBoxLayout(frmSettings)
		self.swTimestampInterval = ui.SecondsWidget(self, "&Time stamp interval:", range=(0.0,60.0), step=0.1)
		layoutSettings.addWidget(self.swTimestampInterval)
		self.swChunkInterval = ui.SecondsWidget(self, "&Chunk interval:", range=(0.0,3600.0), step=0.1)
		layoutSettings.addWidget(self.swChunkInterval)
		self.swPlayChunkDelay = ui.SecondsWidget(self, "&Play chunk delay:", range=(0.0,3600.0), step=0.1)
		layoutSettings.addWidget(self.swPlayChunkDelay)
		self.lsTimerRingSize = ui.LabeledSpinner(self, "Timer ring size:", QtGui.QSpinBox)
		self.lsTimerRingSize.setRange(0, 100000)
		self.lsTimerRingSize.setValue(200)
		self.lsTimerRingSize.setSingleStep(10)
		layoutSettings.addWidget(self.lsTimerRingSize)

		self.swTimestampInterval.setValue(0.4)
		self.swChunkInterval.setValue(1.0)
		self.swPlayChunkDelay.setValue(2.0)

		self.addLeftSide(frmSettings)

		self.setWindowTitle("Server - SyncedMusic")
