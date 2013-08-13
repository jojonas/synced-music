from PyQt4 import QtGui, QtCore
import sys
import logging
import logging.handlers

# http://stackoverflow.com/questions/12214801/python-print-a-string-as-hex-bytes
def hex(s):	
	return ":".join("{0:02x}".format(ord(c)) for c in s)
# --

LOG_FORMAT = "%(asctime)s.%(msecs)d %(filename)s:%(lineno)d %(levelname)s :: %(message)s"
DATE_FORMAT = "%d.%m.%Y %H:%M:%S"

LEVELS = {"error": logging.ERROR, "warning": logging.WARN, "info": logging.INFO, "debug": logging.DEBUG}

class TextLog(QtGui.QTreeWidget, logging.Handler):
	signalHandle = QtCore.pyqtSignal(logging.LogRecord)

	def __init__(self, parent=None):
		QtGui.QTreeWidget.__init__(self, parent)
		logging.Handler.__init__(self)

		headerItem = QtGui.QTreeWidgetItem()
		headerItem.setData(0,0, QtCore.QString("Level"))
		headerItem.setData(1,0, QtCore.QString("Time"))
		headerItem.setData(2,0, QtCore.QString("Location"))
		headerItem.setData(3,0, QtCore.QString("PID:TID"))
		headerItem.setData(4,0, QtCore.QString("Message"))
		self.setHeaderItem(headerItem)
		self.setRootIsDecorated(False)
		self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)

		self.logger = logging.getLogger(__name__)
		self.logger.addHandler(self)

		self.max_entries = 1000

		self.colors = { 
		   logging.DEBUG:	QtGui.QColor(200,255,200), 
		   logging.INFO:	QtGui.QColor(200,220,255),
		   logging.WARNING: QtGui.QColor(255,255,200),
		   logging.ERROR: QtGui.QColor(255,200,200),
		   logging.CRITICAL: QtGui.QColor(255,100,100)
		}

		self.filter = None

		shortcutCtrlF = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+F"), self)
		shortcutCtrlF.activated.connect(self.filterDialog)

		shortcutCtrlL = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+L"), self)
		shortcutCtrlL.activated.connect(self.levelDialog)

		self.signalHandle.connect(self.handleRecord)

	def handle(self, record):
		self.signalHandle.emit(record)

	@QtCore.pyqtSlot(logging.LogRecord)
	def handleRecord(self, record):
		
		item = QtGui.QTreeWidgetItem()
		item.setData(0,0, QtCore.QString(record.levelname))
		item.setData(1,0, QtCore.QString("%s.%d" % (record.asctime, record.msecs)))
		item.setData(2,0, QtCore.QString("%s:%d (%s)" % (record.filename, record.lineno, record.pathname)))
		item.setData(3,0, QtCore.QString("%d:%d" % (record.process, record.thread)))
		item.setData(4,0, QtCore.QString(record.message))
		
		shown = self.filterMatch(item)

		for i in xrange(self.columnCount()):
			item.setData(i,8, self.colors[record.levelno])


		self.addTopLevelItem(item)

		if shown:
			self.scrollToItem(item)
		else:
			item.setHidden(True)

		while self.topLevelItemCount() > self.max_entries:
			self.takeTopLevelItem(0)

	@QtCore.pyqtSlot()
	def levelDialog(self):
		level, ok = QtGui.QInputDialog.getItem(self, "Logging Level", "Choose logging level (for future logs):", [QtCore.QString(level).toUpper() for level in LEVELS.keys()], editable=False)
		if ok:
			logging.getLogger(__name__).setLevel(LEVELS[str(level.toLower())])

	@QtCore.pyqtSlot()
	def filterDialog(self):
		text, ok = QtGui.QInputDialog.getText(self, "Filter", "Enter part of string to filter (leave empty to disable filtering):", text=(self.filter if self.filter is not None else ""))
		if ok:
			if len(text) == 0:
				self.filter = None
			else:
				self.filter = str(text)
			self.filterAll()

	def filterAll(self):
		for i in xrange(self.topLevelItemCount()):
			item = self.topLevelItem(i)
			item.setHidden(not self.filterMatch(item))
			
	def filterMatch(self, item):
		if self.filter is None:
			return True
		else:
			searchStr = self.filter.lower().strip()
			for columnNo in xrange(self.columnCount()):
				data = str(item.data(columnNo,0).toString().toLower())
				if searchStr in data:
					return True
			return False

	def __del__(self):
		self.logger.removeHandler(self)
		QtGui.QTreeWidget.__del__(self)

def setup_logger(logger, lvl, stdout=True):
	logger.setLevel(LEVELS[lvl.lower()])
	if stdout:
		stdoutHandler = logging.StreamHandler(sys.stdout)
		formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
		stdoutHandler.setFormatter(formatter)
		logger.addHandler(stdoutHandler)
	
def getLogger():
	return logging.getLogger(__name__)