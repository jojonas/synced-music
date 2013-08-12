from PyQt4 import QtCore, QtGui
from ..util import log, metrix, ui

class Widget(ui.Widget):
	def setup(self):
		frmServerSelection = QtGui.QGroupBox("Server Selection", self)
		layoutServerSelection = QtGui.QHBoxLayout(frmServerSelection)
		lblServer = QtGui.QLabel("&Server / Host name:", frmServerSelection)
		self.txtServer = QtGui.QLineEdit(frmServerSelection)
		lblServer.setBuddy(self.txtServer)
		self.btnConnect = QtGui.QPushButton("&Connect")
		self.txtServer.returnPressed.connect(self.btnConnect.click)
		layoutServerSelection.addWidget(lblServer)
		layoutServerSelection.addWidget(self.txtServer)
		layoutServerSelection.addWidget(self.btnConnect)
		
		self.addLeftSide(frmServerSelection)
		
		frmControls = QtGui.QGroupBox("Controls", self)
		layoutControls = QtGui.QHBoxLayout(frmControls)
		self.btnResync = QtGui.QPushButton("&Resync", frmControls)
		layoutControls.addWidget(self.btnResync)

		self.addLeftSide(frmControls)

		frmSettings = QtGui.QGroupBox("Settings", self)
		layoutSettings = QtGui.QVBoxLayout(frmSettings)
		self.swOffset = ui.SecondsWidget(self, "&Offset:", range=(-60.0, +60.0), step=0.010)
		layoutSettings.addWidget(self.swOffset)
		self.lsTimerRingSize = ui.LabeledSpinner(self, "Timer ring size:", QtGui.QSpinBox)
		self.lsTimerRingSize.setRange(0, 100000)
		self.lsTimerRingSize.setValue(200)
		
		layoutSettings.addWidget(self.lsTimerRingSize)

		self.addLeftSide(frmSettings)

		self.setWindowTitle("Client - SyncedMusic")

		self.txtServer.setFocus()