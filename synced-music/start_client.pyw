from PyQt4 import QtCore, QtGui
import sys
from core.client import ui, network
from core.util import log, profiling
import threading

retval = 0

with profiling.Profiling(False):
	logger = log.getLogger()
	log.setup_logger(logger, "info", True)

	try:
		app = QtGui.QApplication(sys.argv)

		widget = ui.Widget(logger)
		widget.setWindowIcon(QtGui.QIcon('logo.png'))
		widget.resize(800,600)
	
		client = network.SyncedMusicClient(logger)

		widget.metrix.add("Threads", lambda: [thread.name for thread in threading.enumerate()])
		widget.metrix.add("Time", lambda: client.timer.time())
		widget.metrix.add("Time ratio", lambda: client.timer.m)	
		widget.metrix.add("Time start", lambda: client.timer.a)	
		widget.metrix.add("Playback queue length", lambda: client.soundWriter.getEnqueued())
		widget.metrix.add("Timer data points", client.timer.dataLength)
	
		def connectToServer():
			client.connect(widget.txtServer.text())

		widget.btnConnect.clicked.connect(connectToServer)
		widget.btnResync.clicked.connect(client.timer.reset)
		widget.swOffset.valueChanged.connect(client.setPlaybackOffset)
		widget.lsTimerRingSize.valueChanged.connect(client.timer.setRingsize)

		widget.swOffset.emitChanged()
		widget.lsTimerRingSize.emitChanged()

		def quit(a):
			client.stop()

		widget.closeEvent = quit

		client.start()
		retval = app.exec_()

	except Exception as e:
		logger.exception(e)
		
sys.exit(retval)

