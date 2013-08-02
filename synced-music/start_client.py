from PyQt4 import QtCore, QtGui
import sys
from core.client import ui, network
from core.util import log


try:
	app = QtGui.QApplication(sys.argv)
	widget = ui.Widget()
	client = network.SyncedMusicClient(widget.logger)
	widget.metrix.add("time", lambda: client.timer.time())
	widget.metrix.add("time ratio", lambda: client.timer.m)
	def connectToServer():
		client.connect(widget.txtServer.text())
	widget.btnConnect.clicked.connect(connectToServer)
	def quit(a,b):
		client.quit()
	widget.closeEvent = quit
	client.start()
	sys.exit(app.exec_())
except Exception as e:
	log.getLogger().exception(e)
