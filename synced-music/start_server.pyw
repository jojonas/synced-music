from PyQt4 import QtCore, QtGui
import sys
from core.server import ui, network
from core.util import log, profiling
import threading

retval = 0

with profiling.Profiling(False):
	logger = log.getLogger()
	log.setup_logger(logger, "info", True)

	try:
		app = QtGui.QApplication(sys.argv)

		widget = ui.Widget(logger)
		widget.setWindowIcon(QtGui.QIcon('logo_red.png'))
		widget.resize(800,600)
	
		server = network.SyncedMusicServer(logger)

		widget.metrix.add("Threads", lambda: [thread.name for thread in threading.enumerate()])
		widget.metrix.add("Time", lambda: server.timer.time())
		widget.metrix.add("Time ratio", lambda: server.timer.m)
		widget.metrix.add("Time start", lambda: server.timer.a)
		widget.metrix.add("Peers", lambda: [s.getsockname() for s in server.readSocketList])
		widget.metrix.add("Timer data points", server.timer.dataLength)

		def quit(a):
			logger.info("Quit!")
			server.stop()

		widget.closeEvent = quit

		widget.btnResync.clicked.connect(server.timer.reset)
		widget.swChunkInterval.valueChanged.connect(server.setChunkInterval)
		widget.swPlayChunkDelay.valueChanged.connect(server.setPlayChunkDelay)
		widget.swTimestampInterval.valueChanged.connect(server.setTimestampInterval)
		widget.lsTimerRingSize.valueChanged.connect(server.timer.setRingsize)

		widget.cmbDevice.currentIndexChanged.connect(server.soundReader.openDevice)
	
		widget.swChunkInterval.emitChanged()
		widget.swPlayChunkDelay.emitChanged()
		widget.swTimestampInterval.emitChanged()
		widget.lsTimerRingSize.emitChanged()

		server.start()
		retval = app.exec_()

	except Exception as e:
		logger.exception(e)

sys.exit(retval)