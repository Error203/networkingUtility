import traceback
import socket
import hex_dump
from select import select
import argparse


class Client:


	def __init__(self, connect_ip: str, connect_port: int, buffer_length: int=8192, hex_dumper: bool=False) -> object:
		self.ip = connect_ip
		self.port = connect_port
		self.buffer_length = buffer_length
		self.hex_dumper = hex_dumper

		if self.hex_dumper:
			self.hex_dump = hex_dump.Hex(self.hex_dumper).hex_dump


	def send_data(self, data: [bytes, str], intercept: bool=False) -> int:
		if not isinstance(data, bytes):
			data = data.encode("utf-8")

		if intercept:
			data += bytes(input("#: "), "utf-8")

		data += b"\r\n"

		self.client.settimeout(1)

		print("\rsending...")
		try:
			self.client.send(data)
		except BrokenPipeError:
			print("connection broken by server")
			return 1

		return 0


	def receive_data(self) -> bytes:
		print("\rreceiving...")
		data_buffer = self.client.recv(self.buffer_length)

		if self.hex_dumper:
			self.hex_dump(data_buffer)

		if not data_buffer:

			self.break_pipe()

			return 1

		return data_buffer


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

	argument_parser.add_argument("ip", type=str, help="ip address")
	argument_parser.add_argument("port", type=int, help="port")
	argument_parser.add_argument("-d", "--hexdump", action="store_true", help="hexdump stream")
	argument_parser.add_argument("-b", "--buffer", type=int, default=8192, help="buffer size")

	parsed_arguments = argument_parser.parse_args()

	client = Client(connect_ip=parsed_arguments.ip, connect_port=parsed_arguments.port, buffer_length=parsed_arguments.buffer, hex_dumper=True)
	client.start()
	while True:

		try:
			code = client.send_data(input("#: "))

			# received_data = client.receive_data()

			# if not received_data:
				# break

			if code:
				break

		except KeyboardInterrupt:
			print("\rconnection broken by client")

			break

	client.break_pipe()
