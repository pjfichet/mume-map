import sys
import logging 
from .map import Map

# levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
format = '%(asctime)s %(levelname)s %(funcName)s: %(message)s'
logging.basicConfig(filename='map.log', format=format, level=logging.INFO)
logger = logging.getLogger(__name__)

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

sys.stderr = StreamToLogger(logger, logging.CRITICAL)

