import Tkinter
import logging

class TextLog(Tkinter.Text, logging.Handler):
	def __init__(self, master=None):
		Tkinter.Text.__init__(self, master=master)
		logging.Handler.__init__(self)

		logger = logging.getLogger(__name__)
		logger.addHandler(self)

		frm = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", "%d.%m.%Y %H:%M:%S") 
		self.setFormatter(frm)

	def handle(self, record):
		msg = self.format(record)
		self.insert(Tkinter.END, msg + "\n")

	def flush(self):
		self.update_idletasks()

def getLogger():
	return logging.getLogger(__name__)