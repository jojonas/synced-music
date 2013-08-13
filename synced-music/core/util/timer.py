import time, datetime
import platform
import log

from PyQt4 import QtCore

def linearRegression(x, y):
	Sxx = sum(xi*xi for xi in x)
	Sy = sum(y)
	Sx = sum(x)
	Sxy = sum(xi*yi for xi, yi in zip(x,y))
	
	S = len(x)
	
	delta = S*Sxx - Sx*Sx
	
	a = (Sxx*Sy - Sx*Sxy)/delta
	m = (S*Sxy - Sx*Sy)/delta
	
	return (a,m)


if platform.system() == "Windows":
	def clock():
		return time.clock()

else:
	def clock():
		return time.time()


class HighPrecisionTimer:
	def __init__(self):
		self.minimumDataCount = 50
		self.ringSize = 200
		self.reset()
		self.update()

	def reset(self):
		self.a = time.time()
		self.m = 1
		self.firstClock = clock()
		self.dataTime = []
		self.dataClock = []

	def clock(self):
		return clock() - self.firstClock

	def update(self, time_now=None):
		if time_now == None:
			time_now = time.time()
		#log.getLogger().debug("update timer, now: %f", time_now)
		self.dataClock.append(self.clock())
		self.dataTime.append(time_now)

		self.dataClock = self.dataClock[-self.ringSize:]
		self.dataTime = self.dataTime[-self.ringSize:]
		self._updateRegression()
		
	def _updateRegression(self):
		if len(self.dataClock) > 1:
			self.a, self.m = linearRegression(self.dataClock, self.dataTime)
		elif len(self.dataClock) == 1:
			self.a = self.dataTime[0]
			self.m = 1
			
	def time(self):
		if len(self.dataClock) > self.minimumDataCount:
			return self.clock() * self.m + self.a
		else:
			return clock() + self.a
			
	def dataLength(self):
		return len(self.dataTime)

	@QtCore.pyqtSlot(int)
	def setRingsize(self, value):
		self.ringSize = value

if __name__=="__main__":
	import random
	timer = HighPrecisionTimer()
	for i in xrange(100):
		if i % 10 == 0:
			timer.update()
		print "%.5f" % timer.time()
		time.sleep(random.random()*0.01)
			