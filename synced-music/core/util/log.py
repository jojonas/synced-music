from PyQt4 import QtGui
import logging

class TextLog(QtGui.QListWidget, logging.Handler):
	def __init__(self, parent=None):
		QtGui.QListWidget.__init__(self, parent)
		logging.Handler.__init__(self)

		logger = logging.getLogger(__name__)
		logger.addHandler(self)

		frm = logging.Formatter("%(asctime)s.%(msecs)d %(filename)s:%(lineno)d %(levelname)s :: %(message)s", "%d.%m.%Y %H:%M:%S") 
		self.setFormatter(frm)

	def handle(self, record):
		msg = self.format(record)
		self.addItem(msg)

def getLogger():
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.DEBUG)
	return logger