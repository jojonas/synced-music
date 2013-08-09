import contextlib

# ================== FRAMEWORKS START ==================

try:
	import yappi
except ImportError:
	YappiProfiling = None
else:
	@contextlib.contextmanager
	def YappiProfiling():
		yappi.start()
		yield
		yappi.stop()
		yappi.print_stats()

try:
	import cProfile
except ImportError:
	cProfileProfiling = None
else:
	@contextlib.contextmanager
	def cProfileProfiling():
		pr = cProfile.Profile()
		pr.enable()
		yield
		pr.disable()
		pr.print_stats()

try:
	import profiling
except ImportError:
	profilingProfiling = None
else:
	@contextlib.contextmanager
	def profilingProfiling():
		pr = cProfile.Profile()
		pr.enable()
		yield
		pr.disable()
		pr.print_stats()


# ================== FRAMEWORK PRIORITIES ==================

FRAMEWORKS = [YappiProfiling, cProfileProfiling, profilingProfiling]

# ================== FRAMEWORKS END ==================


@contextlib.contextmanager
def NoProfiling():
	yield

@contextlib.contextmanager
def Profiling(enabled=True, frameworkList=None):
	if frameworkList is None:
		frameworkList = FRAMEWORKS
	currentFramework = NoProfiling

	if enabled:
		print "Profiling enabled."
		for framework in frameworkList:
			if framework != None:
				currentFramework = framework
				print "Profiling framework %s available" % framework.__name__
				break
			else:
				print "Profiling framework %s unavailable" % framework.__name__
	else:
		print "Profiling disabled."

	with currentFramework():
		yield

