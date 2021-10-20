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


	def receive_header(self):


		try:

			file_header = self.socket.recv(4096)
			self.log.debug("mode: decode")
			decoded_structure = self.decoder.decode(file_header.decode("utf-8"))

		except json.JSONDecodeError:

			if len(file_header) > 4096:

				self.log.error(f"header length is too long: {len(file_header)} bytes")

			else:

				self.log.error(f"header can be wrong or broken")

		except Exception as e:

			self.log.exception(e)

		else:

			self.log.debug("header received")

			return decoded_structure


	def send_header(self, header_dictionary):


			try:

				local_header = header_dictionary

				if len(local_header) > 4096:

					self.log.warning(f"header length is too long: {len(local_header)} bytes")

				self.log.debug("mode: send")
				self.socket.send(bytes(self.encoder.encode(local_header), encoding="utf-8"))

			except json.JSONDecodeError:

				self.log.error("input data is incorrect and can't be encoded")

			except Exception as e:

				self.log.exception(e)

			else:

				self.log.debug("header sent")


	def send_data(self, data):


		try:

			if type(data) is not bytes:

				data = bytes(data, encoding="utf-8")

			if len(data) <= 4096:

				self.send_header({"packet_size" : len(data), "mode" : "one_packet"})
				self.socket.send(data)

			elif len(data) > 4096:

				self.send_header({"packet_size" : len(data), "mode" : "multiple_packet"})

				for i in range(0, len(data) + 1, 4096):

					self.socket.send(data)

			self.log.debug(f"sent {len(data)} bytes of data")

		except Exception as e:

			self.log.exception(e)

		else:

			self.log.debug("data sent successfully")


	def receive_data(self):


		try:

			header = self.receive_header()

			if header["mode"] == "one_packet":

				packet_size = header["packet_size"]
				self.log.debug(f"mode: one packet ({packet_size} B)")
				data = self.socket.recv(4096)
				data = data

				return data

			elif header["mode"] == "multiple_packet":

				packet_size = header["packet_size"]
				self.log.debug(f"mode: multiple packets ({packet_size} B)")
				data_collection = b""

				for i in range(0, packet_size + 1, 4096):

					data_collection += self.socket.recv(4096)

				return data_collection

			else:

				self.log.debug(f"header is not satisfying\r\n{header}")

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
