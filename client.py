import traceback
import socket
import hex_dump
from select import select


class Client:


	def __init__(self, connect_ip: str="127.0.0.1", connect_port: int=9876, buffer_length: int=8192, hex_dumper: bool=False) -> object:
		self.ip = connect_ip
		self.port = connect_port
		self.buffer_length = buffer_length
		self.hex_dumper = hex_dumper

		if self.hex_dumper:
			self.hex_dump = hex_dump.Hex(self.hex_dumper).hex_dump


	def send_data(self, data: [bytes, str]) -> int:
		if not isinstance(data, bytes):
			data = data.encode("utf-8")

		data += b"\r\n"

		print("\rsending...")
		self.client.send(data)

		return 1


	def receive_data(self) -> bytes:
		print("\rreceiving...")
		data_buffer = self.client.recv(self.buffer_length)

		if self.hex_dumper:
			self.hex_dump(data_buffer)

		return data_buffer


	def break_pipe(self) -> None:
		if self.client.fileno() != -1:
			print("\rclosing socket...")
			self.client.close()

			print("\rcleaning up...")
			del(self.client)

			exit(254)


	def start(self) -> None:
		print("\rinitializng...")
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.client.connect((self.ip, self.port))


if __name__ == '__main__':
	client = Client(hex_dumper=True)
	client.start()
	while True:
		client.send_data(input("#: "))
	client.break_pipe()
