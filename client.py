import traceback
import socket
from modules import hex_dump
from select import select
import argparse
import sys


class Client:


	def __init__(self, connect_ip: str, connect_port: int, buffer_length: int=8192, hex_dumper: bool=False, file_path: str=None) -> object:
		self.ip = connect_ip
		self.port = connect_port
		self.buffer_length = buffer_length
		self.hex_dumper = hex_dumper

		if file_path:
			self.send_file(file_path)

			exit(0)

		if self.hex_dumper:
			self.hex_dump = hex_dump.Hex(self.hex_dumper).hex_dump


	def send_data(self, data: [bytes, str], intercept: bool=False) -> int:
		if not isinstance(data, bytes):
			data = data.encode("utf-8")

		if intercept:
			data += bytes(input("#: "), "utf-8")

		data += b"\r\n"

		self.client.settimeout(1)

		try:
			self.client.send(data)
			
			print("\rsent")
		except BrokenPipeError:
			print("connection broken by server")
			return 1

		return 0


	def receive_data(self) -> bytes:
		data_buffer = self.client.recv(self.buffer_length)

		print("\rreceived")
		
		if self.hex_dumper:
			self.hex_dump(data_buffer)

		if not data_buffer:

			self.break_pipe()

			return 1

		return data_buffer


	def send_file(self, file_path) -> int:
		print("sending file .../{}".format(file_path.split("/")[-1]))
		with open(file_path, "rb") as file:
			self.send_data(file.read())

		del(file)


	def break_pipe(self) -> None:
		if self.client.fileno() != -1:
			print("\rclosing socket...")
			self.client.close()

			print("\rcleaning up...")
			del(self.client)


	def start(self) -> None:
		print("\rinitializng...")
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.client.connect((self.ip, self.port))


if __name__ == '__main__':

	argument_parser = argparse.ArgumentParser(description="tool to work with some protocols in internet")

	argument_parser.add_argument("ip", type=str, help="ip address or dns server")
	argument_parser.add_argument("port", type=int, help="port")
	argument_parser.add_argument("-d", "--hexdump", action="store_true", help="hexdump stream")
	argument_parser.add_argument("-b", "--buffer", type=int, default=8192, help="buffer size")
	argument_parser.add_argument("-f", "--file", type=str, default=None, help="path to the file to send")
	argument_parser.add_argument("-s", "--secure", action="store_true", help="use secure connection (paramiko) or not")

	parsed_arguments = argument_parser.parse_args()

	client = Client(connect_ip=parsed_arguments.ip, connect_port=parsed_arguments.port, buffer_length=parsed_arguments.buffer, hex_dumper=True, file_path=parsed_arguments.file)
	client.start()
	while True:

		try:
			if not sys.stdin.isatty():
				client.send_data("".join(sys.stdin))
				client.receive_data()

				break

			else:
				code = client.send_data(input("#: "))
				client.receive_data()

				if code:

					break


		except KeyboardInterrupt:
			print("\rconnection broken by client")

			break

	client.break_pipe()
