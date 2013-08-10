import time, datetime
import platform
import log

def linear_regression(x, y):
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
	class HighPrecisionTimer:
		def __init__(self):
			self.minimum_data_count = 5
			self.ring_size = 200

			self.reset()
			self.update()

		def reset(self):
			self.a = time.time()
			self.m = 1
			
			self.data_time = []
			self.data_clock = []

		def update(self, time_now=None):
			if time_now == None:
				time_now = time.time()
			#log.getLogger().debug("update timer, now: %f", time_now)
			self.data_clock.append(time.clock())
			self.data_time.append(time_now)
			self.data_clock = self.data_clock[-self.ring_size:]
			self.data_time = self.data_time[-self.ring_size:]
			self._updateRegression()
		
		def _updateRegression(self):
			if len(self.data_clock) > 1:
				self.a, self.m = linear_regression(self.data_clock, self.data_time)
			elif len(self.data_clock) == 1:
				self.a = self.data_time[0]
				self.m = 1
			
		def time(self):
			if len(self.data_clock) > self.minimum_data_count:
				return time.clock() * self.m + self.a
			else:
				return time.clock() + self.a
			
		def dataLength(self):
		   return len(self.data_time)
			
else:
	class HighPrecisionTimer:
		def __init__(self):
			self.reset()

		def reset(self):
			self.a = time.time()
			self.m = 1.0

		def update(self):
			pass
			
		def time(self):
			return time.time()
		
		def dataLength(self):
			return 0

if __name__=="__main__":
	import random
	timer = HighPrecisionTimer()
	for i in xrange(100):
		if i % 10 == 0:
			timer.update()
		print "%.5f" % timer.time()
		time.sleep(random.random()*0.01)
			