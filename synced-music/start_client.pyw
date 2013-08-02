from PyQt4 import QtCore, QtGui
import sys
from core.client import ui, network
from core.util import log


logger = log.getLogger()
log.setup_logger(logger, "debug", True)

try:
	app = QtGui.QApplication(sys.argv)

	widget = ui.Widget(logger)
	widget.setWindowIcon(QtGui.QIcon('logo.png'))
	widget.resize(800,600)
	
	client = network.SyncedMusicClient(logger)

	widget.metrix.add("time", lambda: client.timer.time())
	widget.metrix.add("time ratio", lambda: client.timer.m)

	def connectToServer():
		client.connect(widget.txtServer.text())
	widget.btnConnect.clicked.connect(connectToServer)

	def quit(a):
		client.quit()
	widget.closeEvent = quit

	client.start()

	sys.exit(app.exec_())

except Exception as e:
	logger.exception(e)
