import qlogger
import socket


class Client:


	def __init__(self, ip, port, log_level=qlogger.logging.INFO):
		try:
			self.log = qlogger.Logger("client log", log_level).get_logger("client")
			self.ip = ip
			self.port = port
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.log.info("initialized client")
		except Exception as e:
			self.log.exception(e)

			exit(1)


	def start_client(self):
		try:
			self.socket.connect((self.ip, self.port))
			self.log.info(f"connected -> {self.ip}:{self.port}")
		except Exception as e:
			self.log.exception(e)

			self.break_pipe()
			exit(1)
		else:
			self.log.debug("started without exceptions")


	def receive_file(self):
		try:
			file_header = self.socket.recv(1024)
			file_header = file_header.decode()
			header = file_header.replace(" ", "").strip().split(";")
			file_format = header[0]
			total_file_size = header[1]
			self.log.debug(f"header -> {file_header}")
			# data = 1
			# assembled_file = b""
			# while data:
			# 	packet = self.socket.recv(4096)
			# 	if data < 4096:
			# 		break
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