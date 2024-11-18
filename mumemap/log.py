import sys
import logging 

class StreamToLogger(object):
	"""Fake file-like stream object that redirects writes to a logger instance.
	"""
	def __init__(self, logger, level):
		self.logger = logger
		self.level = level
		self.linebuf = ''

	def write(self, buf):
		for line in buf.rstrip().splitlines():
			self.logger.log(self.level, line.rstrip())

	def flush(self):
		pass

levels = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]

def log(filename='map.log', verbosity=2, redirectstderr=False):
	# levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
	if verbosity > 4:
		verbosity = 4
	format = '%(asctime)s %(levelname)s %(funcName)s: %(message)s'
	logging.basicConfig(filename=filename, format=format, level=levels[verbosity])
	logger = logging.getLogger(__name__)
	if redirectstderr:
		sys.stderr = StreamToLogger(logger, logging.CRITICAL)

