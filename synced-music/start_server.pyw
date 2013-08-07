from PyQt4 import QtCore, QtGui
import sys
from core.server import ui, network
from core.util import log
import threading

logger = log.getLogger()
log.setup_logger(logger, "debug", True)

try:
	app = QtGui.QApplication(sys.argv)

	widget = ui.Widget(logger)
	widget.setWindowIcon(QtGui.QIcon('logo_red.png'))
	widget.resize(800,600)
	
	server = network.SyncedMusicServer(logger)

	widget.metrix.add("Threads", lambda: [thread.name for thread in threading.enumerate()])
	widget.metrix.add("Time", lambda: server.timer.time())
	widget.metrix.add("Time ratio", lambda: server.timer.m)
	widget.metrix.add("Peers", lambda: [s.getsockname() for s in server.readSocketList])

	def quit(a):
		logger.info("Quit!")
		server.quit()
		server.join()

	widget.cmbDevice.currentIndexChanged.connect(server.soundReader.openDevice)
	widget.closeEvent = quit

	server.start()

	sys.exit(app.exec_())

except Exception as e:
	logger.exception(e)
