from PyQt4 import QtCore, QtGui
import sys
from core.server import ui, network
from core.util import log

logger = log.getLogger()
log.setup_logger(logger, "debug", True)

try:
	app = QtGui.QApplication(sys.argv)

	widget = ui.Widget(logger)
	widget.setWindowIcon(QtGui.QIcon('logo_red.png'))
	widget.resize(800,600)
	
	server = network.SyncedMusicServer(logger)

	widget.metrix.add("time", lambda: server.timer.time())
	widget.metrix.add("time ratio", lambda: server.timer.m)
	widget.metrix.add("peers", lambda: [s.getsockname() for s in server.readSocketList])

	def quit(a):
		logger.info("quit!")
		server.quit()

	widget.cmbDevice.currentIndexChanged.connect(server.soundReader.openDevice)
	widget.closeEvent = quit

	server.start()

	sys.exit(app.exec_())

except Exception as e:
	logger.exception(e)
