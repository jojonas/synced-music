from PyQt4 import QtCore, QtGui
import sys
from core.server import ui, network
from core.util import log


app = QtGui.QApplication(sys.argv)
try:
	widget = ui.Widget()
	server = network.SyncedMusicServer(widget.logger)
	widget.metrix.add("time", lambda: server.timer.time())
	widget.closeEvent = server.quit
except Exception as e:
	log.getLogger().exception(e)

sys.exit(app.exec_())