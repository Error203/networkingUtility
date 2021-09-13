import qlogger
import socket
import time
import json


class Client:


	def __init__(self, ip, port, log_level=qlogger.logging.INFO):
		try:
			self.log = qlogger.Logger("client log", log_level).get_logger("client")
			self.ip = ip
			self.port = port
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
			self.log.debug(f"\nheader: {decoded_structure}\ntype: {type(decoded_structure)}")
			# file_header = file_header.decode()
			# header = file_header.replace(" ", "").strip().split(";")
			# file_format = header[0]
			# total_file_size = header[1]
			# self.log.debug(f"header -> {file_header}")
		except Exception as e:
			self.log.exception(e)

		else:
			self.log.debug("receive_header -> success")

			return decoded_structure


	def send_header(self, header_dictionary):
			try:
				local_header = header_dictionary
				self.log.debug("mode: send")
				self.socket.send(bytes(self.encoder.encode(local_header), encoding="utf-8"))

			except Exception as e:
				self.log.exception(e)
			else:
				self.log.debug("send_header -> success")

				return 0


	def receive_header(self):
		try:
			file_header = self.socket.recv(4096)
			self.log.debug("mode: decode")
			decoded_structure = self.decoder.decode(file_header.decode("utf-8"))
			self.log.debug(f"\nheader: {decoded_structure}\ntype: {type(decoded_structure)}")
			# file_header = file_header.decode()
			# header = file_header.replace(" ", "").strip().split(";")
			# file_format = header[0]
			# total_file_size = header[1]
			# self.log.debug(f"header -> {file_header}")
		except Exception as e:
			self.log.exception(e)

		else:
			self.log.debug("receive_header -> success")

			return decoded_structure


	def receive_file(self):
		try:
			pass
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


	def send_data(self, data):
		try:
			if type(data) is not bytes:
				data = bytes(data, encoding="utf-8")
			if len(data) >= 4096:
				self.send_header({"packet_size" : len(data), "mode" : "one_packet"})
				self.socket.send(data)
			elif len(data) < 4096:
				self.send_header({"packet_size" : len(data), "mode" : "multiple_packet"})
				for i in range(0, len(data) + 1, 4096):
					self.socket.send(data)
			self.log.debug(f"sent {len(data)} bytes of data")
			operation_code = self.receive_header()["operation_code"]
			self.log.debug(f"operation code -> {operation_code}")
		except Exception as e:
			self.log.exception(e)

			self.send_header({"operation_code" : "failed"})
		else:
			self.send_header({"operation_code" : "success"})
			self.log.debug("send_data session -> success")

			return 0


	def receive_data(self):
		try:
			header = self.receive_header()
			if header["mode"] == "one_packet":
				packet_size = header["packet_size"]
				self.log.debug(f"mode -> one packet ({packet_size} B)")
				data = self.socket.recv(4096)
				data = data.decode("utf-8")
				self.log.info(f"accepted info:\n\n\n{data}\n\n")
			elif header["mode"] == "multiple_packet":
				packet_size = header["packet_size"]
				self.log.debug(f"mode -> multiple packets ({packet_size} B)")
				data_collection = b""
				for i in range(0, packet_size + 1, 4096):
					data_collection += self.socket.recv(4096)
				self.log.debug("WARNING, A LOT OF INFORMATION")
				self.log.debug(f"\n{data}")

		except Exception as e:
			self.log.exception(e)

			self.send_header({"operation_code" : "failed"})
		else:
			self.send_header({"operation_code" : "success",})
			self.log.debug("receive_data session -> success")


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
