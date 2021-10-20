import qlogger
import socket
import time
import json
from os import path


class Client:


	def __init__(self, ip, port, eternity, log_level=qlogger.logging.INFO):


		try:

			self.log = qlogger.Logger(path.join("logs", "client log"), log_level).get_logger("client")
			self.ip = ip
			self.port = port
			self.eternity = eternity
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.log.info("initialized client")
			self.log.debug("initializing json")
			self.decoder = json.JSONDecoder()
			self.log.debug("decoder is ready")
			self.encoder = json.JSONEncoder()
			self.log.debug("encoder is ready")

		except Exception as e:

			self.log.exception(e)
			self.log.critical("failed on initializing")

			exit(1)


	def start_client(self):


		try:

			self.socket.connect((self.ip, self.port))
			self.log.info(f"connected -> {self.ip}:{self.port}")

		except ConnectionRefusedError:

			self.log.debug("connection refused")

			if self.eternity:

				while True:

					try:

						self.socket.connect((self.ip, self.port))

					except ConnectionRefusedError:

						self.log.debug("connection refused, retrying in 5 seconds")
						time.sleep(5)

						continue

					except Exception as e:

						self.log.exception(e)

						break

					else:

						self.log.info(f"connected -> {self.ip}:{self.port}")

						break

			else:

				self.log.error("server refused the connection")

		except Exception as e:

			self.log.exception(e)

			self.break_pipe()
			exit(1)

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
