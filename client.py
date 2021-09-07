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
		else:
			self.log.debug("ended without exceptions")

			exit(0)
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