import logging
from os import mkdir, listdir, path
from time import strftime
import json


class Logger:
	def __init__(self, directory_name=None, level=logging.INFO, file_stream=True):

		"""
		directory_name=None
		Directory name where is stored logs
		"""

		self.file_stream = file_stream

		if self.file_stream:

			if not directory_name:
				directory_name = "logs"

			if directory_name not in listdir("."):
				mkdir(directory_name) # if there is no Logs directory in the root

			self.directory_name = directory_name

		self.level = level


	def get_logger(self, name: str="unmarked") -> logging.Logger:
		"""
		Get simple logger.
		"""
		file_name = strftime("[%d-%m-%y] %H-%M-%S.log") # name of logger, can be changed

		logger = logging.getLogger(name) # logger
		logger.setLevel(logging.DEBUG) # set level of general logger
		stream_handler = logging.StreamHandler() # stream handler to monitor errors to the console
		formatter = logging.Formatter(fmt="[%(name)s] %(levelname)s: %(message)s") # format of logs
		stream_handler.setFormatter(formatter) # setting format
		stream_handler.setLevel(self.level) # setting level debug to debug this code

		if self.file_stream:

			file_handler = logging.FileHandler(path.join(self.directory_name, file_name)) # write errors and info to the file
			file_formatter = logging.Formatter(fmt="[%(asctime)s] %(name)s, %(levelname)s: %(message)s")
			file_handler.setFormatter(file_formatter)
			file_handler.setLevel(logging.DEBUG)
			logger.addHandler(file_handler)

		logger.addHandler(stream_handler) # add handler to handle exceptions

		return logger # return ready logger to work with
