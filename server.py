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
		except Exception as e:
			self.log.exception(e)

			exit(1)
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