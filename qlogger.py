import logging
from os import mkdir, listdir, path
from time import strftime
import json


sep = path.sep


class Logger:


	def __init__(self, directory_name=None, level=logging.INFO, file_stream=True):

		if file_stream:

			self.dirs = directory_name.split(sep)

			if len(self.dirs) <= 1:

				if not directory_name:
					directory_name = "logs"

				if directory_name not in listdir("."):
					mkdir(directory_name)

			if len(self.dirs) > 1:
				
				if not path.exists(directory_name):

					for i in range(len(self.dirs)):

						real_path = sep.join(self.dirs[0:i + 1])
						mkdir(real_path)

			else:

				print("no matching", self.dirs)

		self.directory_name = directory_name
		self.level = level
		self.file_stream = file_stream


	def get_logger(self, name: str="unmarked") -> logging.Logger:


		file_name = strftime("[%d-%m-%y] %H-%M-%S.log")

		logger = logging.getLogger(name)
		logger.setLevel(logging.DEBUG)
		stream_handler = logging.StreamHandler()
		formatter = logging.Formatter(fmt="[%(name)s] %(levelname)s: %(message)s")
		stream_handler.setFormatter(formatter)
		stream_handler.setLevel(self.level)

		if self.file_stream:

			file_handler = logging.FileHandler(path.join(self.directory_name, file_name))
			file_formatter = logging.Formatter(fmt="[%(asctime)s] %(name)s, %(levelname)s: %(message)s")
			file_handler.setFormatter(file_formatter)
			file_handler.setLevel(logging.DEBUG)
			logger.addHandler(file_handler)

		logger.addHandler(stream_handler)

		return logger
