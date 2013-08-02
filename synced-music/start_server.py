from PyQt4 import QtCore, QtGui
import sys
from core.server import ui, network
from core.util import log


try:
	app = QtGui.QApplication(sys.argv)
	widget = ui.Widget()
	server = network.SyncedMusicServer(widget.logger)
	widget.metrix.add("time", lambda: server.timer.time())
	def quit(a,b):
		server.quit()
	widget.closeEvent = quit
	server.start()
	sys.exit(app.exec_())
except Exception as e:
	log.getLogger().exception(e)
