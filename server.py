import qlogger
import socket
import time
import json
from os import path


class Server:


	def __init__(self, ip, port, log_level=qlogger.logging.INFO):


		try:

			self.log = qlogger.Logger(path.join("logs", "server log"), log_level).get_logger("server")
			self.ip = ip
			self.port = port
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.log.info("initialized server")


		except Exception as e:

			self.log.exception(e)
			self.log.critical("failed on initializing")

			exit(1)


	def start_server(self, to_listen=1):


		try:

			self.socket.bind((self.ip, self.port))
			self.socket.listen(to_listen)
			self.log.info(f"server started ({self.ip}:{self.port})")
			self.connected_client, self.address = self.socket.accept()
			self.log.info(f"accepted connection ({self.address[0]}:{self.address[1]})")

		except Exception as e:

			self.log.exception(e)

		else:

			self.log.debug("started without exceptions")


	def send_data(self, data):


		try:

			if not isinstance(data, bytes):

				data = bytes(data, encoding="utf-8")

			data += b"\r\n"

			self.connected_client.send(data)

		except Exception as e:

			self.log.exception(e)

		else:

			self.log.debug(f"successfully sent {len(data)} bytes of data")


	def receive_data(self):


		try:

			data_buffer = b""
			received_page = self.connected_client.recv(4096)
			data_buffer += received_page

			while not received_page < 4096:

				data_buffer += self.connected_client.recv(4096)

		except KeyboardInterrupt:

			self.log.info("captured ")

			break

		except Exception as e:

			self.log.exception(e)

		else:

			self.log.debug("data received successfully")


	def break_pipe(self):

		try:

			file_descriptor = self.socket.fileno()

			if file_descriptor != -1:

				detached_fileno = self.socket.detach()
				self.log.info(f"closed active connection -> fileno: {detached_fileno}")

			elif file_descriptor == -1:

				self.log.error("connection already closed")

		except Exception as e:
			
			self.log.exception(e)