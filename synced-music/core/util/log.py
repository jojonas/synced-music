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

class TextLog(QtGui.QListWidget, logging.Handler):
	def __init__(self, parent=None):
		QtGui.QListWidget.__init__(self, parent)
		logging.Handler.__init__(self)

		self.logger = logging.getLogger(__name__)
		self.logger.addHandler(self)

		formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT) 
		self.setFormatter(formatter)

		self.max_entries = 10000

	def handle(self, record):
		msg = self.format(record)
		self.addItem(msg)
		while self.count() > self.max_entries:
			self.takeItem(0)

	def __del__(self):
		self.logger.removeHandler(self)
		QtGui.QListWidget.__del__(self)

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