import qlogger
import socket


class Server:


	def __init__(self, ip, port, log_level=qlogger.logging.INFO):
		self.log = qlogger.Logger("server log", log_level).get_logger("server")
		self.ip = ip
		self.port = port
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.log.info("initialized server")


	def start_server(self, to_listen=1):
		try:
			self.socket.bind((self.ip, self.port))
			self.socket.listen(to_listen)
			self.log.info(f"server started -> {self.ip}:{self.port}")
			self.connected_client, self.address = self.socket.accept()
			self.log.info(f"accepted connection -> {self.address[0]}:{self.address[1]}")
		except KeyboardInterrupt:
			self.log.info("captured ^C")
			self.break_pipe()
		except Exception as e:
			self.log.exception(e)

			exit(1)
			self.break_pipe()
		else:
			self.log.debug("started without exceptions")


	def send_file(self, path_to_file):
		try:
			file = open(path_to_file, "rb")
			file_format = file.name.split(".")
			file = file.read()
			file_header = list()
			if len(file_format) >= 2:
				file_header.append(str(file_format[-1]))
				self.log.debug(f"file format is {file_format[-1]}")
			else:
				file_header.append("unsigned")
				self.log.debug("file format is unsigned")
			file_size = len(file)
			if file_size != 0:
				file_header.append(str(file_size))
				self.log.debug(f"file size is {file_size}")
			else:
				file_header.append(str(0))
				self.log.warning("file size is 0")

			output_header = bytes(";".join(file_header), encoding="utf-8")
			self.connected_client.send(output_header)
			self.log.debug(f"sent header -> {output_header.decode()}")

		except Exception as e:
			self.log.exception(e)
		finally:
			self.break_pipe()


	def break_pipe(self):
		try:
			file_descriptor = self.socket.fileno()
			if file_descriptor != -1:
				detached_fileno = self.socket.detach()
				self.log.info(f"closed active connection -> fileno: {detached_fileno}")

				exit(0)
			elif file_descriptor == -1:
				self.log.error("connection already closed")

				exit(0)
		except Exception as e:
			self.log.exception(e)

			exit(1)