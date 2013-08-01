from PyQt4 import QtCore, QtGui
import sys
from core.client import ui, network
from core.util import log


app = QtGui.QApplication(sys.argv)
try:
	widget = ui.Widget()
	client = network.SyncedMusicClient(widget.logger)
	widget.metrix.add("time", lambda: client.timer.time())
	def connectToServer():
		client.connect(widget.txtServer.text())
	widget.btnConnect.clicked.connect(connectToServer)
	widget.closeEvent = client.quit
except Exception as e:
	log.getLogger().exception(e)

sys.exit(app.exec_())