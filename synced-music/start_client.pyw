from PyQt4 import QtCore, QtGui
import sys
from core.client import ui, network
from core.util import log
import threading

logger = log.getLogger()
log.setup_logger(logger, "debug", True)

try:
	app = QtGui.QApplication(sys.argv)

	widget = ui.Widget(logger)
	widget.setWindowIcon(QtGui.QIcon('logo.png'))
	widget.resize(800,600)
	
	client = network.SyncedMusicClient(logger)

	widget.metrix.add("Threads", lambda: [thread.name for thread in threading.enumerate()])
	widget.metrix.add("Time", lambda: client.timer.time())
	widget.metrix.add("Time ratio", lambda: client.timer.m)
	widget.metrix.add("Playback queue length", lambda: client.soundWriter.soundBufferQueue.qsize())

	def connectToServer():
		client.connect(widget.txtServer.text())
	widget.btnConnect.clicked.connect(connectToServer)

	def quit(a):
		client.quit()
		client.join()

	widget.closeEvent = quit

	client.start()

	sys.exit(app.exec_())

except Exception as e:
	logger.exception(e)
