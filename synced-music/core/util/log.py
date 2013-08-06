from PyQt4 import QtGui
import sys
import logging
import logging.handlers

# http://stackoverflow.com/questions/12214801/python-print-a-string-as-hex-bytes
def hex(s):	
	return ":".join("{0:02x}".format(ord(c)) for c in s)
# --

LOG_FORMAT = "%(asctime)s.%(msecs)d %(filename)s:%(lineno)d %(levelname)s :: %(message)s"
DATE_FORMAT = "%d.%m.%Y %H:%M:%S"

class TextLog(QtGui.QTreeWidget, logging.Handler):
	def __init__(self, parent=None):
		QtGui.QTreeWidget.__init__(self, parent)
		logging.Handler.__init__(self)

		headerItem = QtGui.QTreeWidgetItem()
		headerItem.setData(0,0, "Level")
		headerItem.setData(1,0, "Time")
		headerItem.setData(2,0, "Logger")
		headerItem.setData(3,0, "Location")
		headerItem.setData(4,0, "Message")
		self.setHeaderItem(headerItem)
		self.setRootIsDecorated(False)

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


	def handle(self, record):
		item = QtGui.QTreeWidgetItem()
		item.setData(0,0, record.levelname)
		item.setData(1,0, "%s.%d" % (record.asctime, record.msecs))
		item.setData(2,0, record.name)
		item.setData(3,0, "%s:%d (%s)" % (record.filename, record.lineno, record.pathname))
		item.setData(4,0, record.message)
		
		for i in xrange(self.columnCount()):
			item.setData(i,8, self.colors[record.levelno])
		
		self.addTopLevelItem(item)
		self.resizeColumnToContents(0)
		self.resizeColumnToContents(1)
		self.resizeColumnToContents(2)
		self.scrollToItem(item)
		self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)

		while self.topLevelItemCount() > self.max_entries:
			self.takeTopLevelItem(0)

	def __del__(self):
		self.logger.removeHandler(self)
		QtGui.QTreeWidget.__del__(self)

def setup_logger(logger, lvl, stdout=True):
	levels = {"error": logging.ERROR, "warning": logging.WARN, "info": logging.INFO, "debug": logging.DEBUG}
	logger.setLevel(levels[lvl])
	if stdout:
		stdoutHandler = logging.StreamHandler(sys.stdout)
		formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
		stdoutHandler.setFormatter(formatter)
		logger.addHandler(stdoutHandler)
	
def getLogger(name=None):
	if name is None:
		name = __name__
	return logging.getLogger(name)