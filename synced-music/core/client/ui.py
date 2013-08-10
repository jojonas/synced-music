from PyQt4 import QtCore, QtGui
from ..util import log, metrix, ui

class Widget(ui.Widget):
	def setup(self):
		frmServerSelection = QtGui.QGroupBox("Server Selection", self)
		layoutServerSelection = QtGui.QHBoxLayout(frmServerSelection)
		lblServer = QtGui.QLabel("&server / host name:", frmServerSelection)
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
		lblOffset = QtGui.QLabel("&offset (ms):", frmControls)
		self.spnOffset = QtGui.QSpinBox(frmControls)
		self.spnOffset.setMinimum(-60000.0)
		self.spnOffset.setMaximum(60000.0)
		lblOffset.setBuddy(self.spnOffset)
		layoutControls.addWidget(self.btnResync)
		layoutControls.addWidget(lblOffset)
		layoutControls.addWidget(self.spnOffset)

		self.addLeftSide(frmControls)

		self.setWindowTitle("Client - SyncedMusic")