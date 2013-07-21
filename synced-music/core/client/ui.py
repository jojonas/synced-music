import Tkinter
from ..util import log

class Application(Tkinter.Frame):
	def __init__(self, master=None):
		Tkinter.Frame.__init__(self, master)
		self.pack()
		self.createWidgets()

	def createWidgets(self):
		frmControls = Tkinter.Frame(self)

		self.txtLog = log.TextLog(self)
		self.logger = log.getLogger()
		#self.logger.addHandler(self.txtLog)
		self.txtLog.pack({"side" : "right"})

		self.btnReset = Tkinter.Button(frmControls)
		self.btnReset["text"] = "Hi"
		def x():
			self.logger.warning("Hallo!")
		self.btnReset["command"] = x
		self.btnReset.pack()

		frmControls.pack({"side" : "left"})

	def log(self, message):
		self.txtLog.insert(Tkinter.END, message)
		self.update_idletasks()

def show():
	root = Tkinter.Tk()
	app = Application(master=root)
	app.mainloop()
	root.destroy()

if __name__=="__main__":
	show()
