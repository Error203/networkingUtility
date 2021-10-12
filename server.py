import qlogger
import socket
import time
import json
import subprocess
from os import path


class Server:


	def __init__(self, ip, port, log_level=qlogger.logging.INFO):
		try:
			self.log = qlogger.Logger("server log", log_level).get_logger("server")
			self.ip = ip
			self.port = port
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.log.info("initialized server")
			self.log.debug("initializing json")
			self.encoder = json.JSONEncoder()
			self.log.debug("encoder is ready")
			self.decoder = json.JSONDecoder()
			self.log.debug("decoder is ready")


		except Exception as e:
			self.log.exception(e)
			self.log.critical("failed on initializing")

			exit(1)


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


	def send_header(self, header_dictionary):
		try:
			local_header = header_dictionary
			self.log.debug("mode: send")
			self.connected_client.send(bytes(self.encoder.encode(local_header), encoding="utf-8"))

		except Exception as e:
			self.log.exception(e)

		else:
			self.log.debug("send_header -> success")

			return 0

		finally:
			self.log.debug(local_header)


	def receive_header(self):
		try:
			file_header = self.connected_client.recv(4096)
			self.log.debug("mode: decode")
			decoded_structure = self.decoder.decode(file_header.decode("utf-8"))

		except Exception as e:
			self.log.exception(e)

		else:
			self.log.debug("receive_header -> success")

			return decoded_structure

		finally:
			self.log.debug(f"\nheader: {decoded_structure}\ntype: {type(decoded_structure)}")


	def send_file(self, path_to_file):
		pass


	def send_data(self, data):
		try:
			if type(data) is not bytes:
				data = bytes(data, encoding="utf-8")
			if len(data) <= 4096:
				self.send_header({"packet_size" : len(data), "mode" : "one_packet"})
				self.connected_client.send(data)
			elif len(data) > 4096:
				self.send_header({"packet_size" : len(data), "mode" : "multiple_packet"})
				for i in range(0, len(data) + 1, 4096):
					self.connected_client.send(data)
			self.log.debug(f"sent {len(data)} bytes of data")
			# operation_code = self.receive_header()["operation_code"]
			# self.log.debug(f"operation code -> {operation_code}")
		except Exception as e:
			self.log.exception(e)

			self.send_header({"operation_code" : "error"})
		else:
			# self.send_header({"operation_code" : "success"})
			self.log.debug("send_data session -> success")


	def receive_data(self):
		try:
			header = self.receive_header()
			if header["mode"] == "one_packet":
				packet_size = header["packet_size"]
				self.log.debug(f"mode -> one packet ({packet_size} B)")
				data = self.connected_client.recv(4096)
				data = data.decode("utf-8")
				# self.log.info(f"accepted info:\n\n\n{data}\n\n")

				return data

			elif header["mode"] == "multiple_packet":
				packet_size = header["packet_size"]
				self.log.debug(f"mode -> multiple packets ({packet_size} B)")
				data_collection = b""
				for i in range(0, packet_size + 1, 4096):
					data_collection += self.connected_client.recv(4096)
				# self.log.debug("WARNING, A LOT OF INFORMATION")
				# self.log.debug(f"\n{data}")

				return data_collection

			else:
				self.log.debug(f"header is not satisfying\r\n{header}")
				self.break_pipe()
				exit(1)

		except Exception as e:
			self.log.exception(e)

			self.send_header({"operation_code" : "error"})
		else:
			self.send_header({"operation_code" : "success",})
			self.log.debug("receive_data session -> success")


	def chatting_room(self, nickname="interlocutor:server"):
		dest_nickname = self.receive_header()["nickname"]
		self.log.debug("received header")
		self.send_header({"nickname" : nickname})
		self.log.debug("sent header")
		self.log.info(f"your partner is: {dest_nickname}")
		self.log.debug("header sequence complete")

		while True:
			try:
				accepted_msg = self.receive_data()
				self.log.debug("accepted message")
				self.log.debug(f"{dest_nickname} says: {accepted_msg}")
				print(f"{dest_nickname} says: {accepted_msg}")

				msg = input("msg > ")

				self.send_data(msg)
				self.log.debug("message sent successfully")

				status = self.receive_header()["status"]
				self.send_header({"status" : "continue"})

				if status == "continue":
					continue
				else:
					self.log.info(f"your partner has ended conversation ({status})")
					break

			except Exception as e:
				self.log.exception(e)
				self.send_header({"status" : "error on client side"})

				self.break_pipe()

			except socket.error:
				pass

			except (KeyboardInterrupt, InterruptedError):
				self.send_header({"status" : "client broken the connection"})
				self.log.debug("interrupted")

				self.break_pipe()
				break


	def console_client(self):
		try:
			while True:
				try:
					self.send_data(input("#: ").encode("utf-8"))
					header_output = self.receive_header()
					status_code = header_output["status_code"]
					output = header_output["output"]
					if status_code != 0:
						self.log.info(f"executing error\r\n{output}")
					else:
						self.log.info(f"success\r\n{output}")
				
				except KeyboardInterrupt:
					print("\r\n\r\n")
					self.send_header({"callback_code" : "interrupted"})
					self.log.info("interrupted")
					break

				else:
					self.send_header({"callback_code" : "continue"})

		except Exception as e:
			self.log.exception(e)


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

			exit(1)