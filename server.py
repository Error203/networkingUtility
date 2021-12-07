import socket
from modules import hex_dump
from time import sleep
import selectors
import argparse
from sys import platform
import subprocess


class Server:


	def __init__(self, bind_ip: str="127.0.0.1", bind_port: int=9876, buffer_length: int=8192, \
		max_clients: int=1, hex_dumper: bool=True, interface: bool=False, proxy: bool=False, \
		secure_connection=False) -> object:

		self.ip = bind_ip
		self.port = bind_port
		self.max_clients = max_clients
		self.buffer_length = buffer_length
		self.hex_dumper = hex_dumper
		self.interface = interface

		self.selector = selectors.DefaultSelector()


		if hex_dumper:
			self.hex_dump = hex_dump.Hex(show=self.hex_dumper).hex_dump


	def initialize_server(self) -> socket.socket:
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server.bind((self.ip, self.port))
		self.server.listen(self.max_clients)
		self.selector.register(fileobj=self.server, events=selectors.EVENT_READ, data=self.accept_connection)
		print("initialized")


	def send_data(self, data: bytes, client_endpoint: socket.socket) -> int:
		if not isinstance(data, bytes):
			data = data.encode("utf-8")

		data += b"\r\n"


		client_endpoint.send(data)

		print("sent")


	def handle_interfaces(self) -> str:
		from netifaces import interfaces, ifaddresses
		found_interfaces = list()
		
		for interface in interfaces():
			found_interfaces.append(ifaddresses(interface)[2][0]["addr"])

		print("found interfaces")
		
		return found_interfaces


	def receive_data(self, client_endpoint: socket.socket) -> bytes:
		data_buffer = b""
		client_endpnt = client_endpoint.getpeername()


		data_buffer += client_endpoint.recv(self.buffer_length)

		if self.hex_dumper:
			self.hex_dump(data_buffer)

		if not self.hex_dumper:
			print(data_buffer)

		if not data_buffer:
			self.break_pipe(client_endpoint)
		
		if data_buffer:
			print(f"\rreceived. {client_endpnt[0]}:{client_endpnt[1]}")
		
		return data_buffer


	def accept_connection(self, socket: socket.socket) -> None:
		client, address_info = socket.accept()
		client.setblocking(False)
		print("client: %s:%d" % (address_info[0], address_info[1]))

		self.selector.register(fileobj=client, events=selectors.EVENT_READ, data=self.receive_data)


	def break_pipe(self, socket: socket.socket) -> None:
		if socket.fileno() != -1:
			client_endpnt = socket.getpeername()
			socket.close()
			print(f"socket closed. {client_endpnt[0]}:{client_endpnt[1]}")

			self.selector.unregister(socket)
			del(socket)
			print(f"\rcleaned up. {client_endpnt[0]}:{client_endpnt[1]}")


	def config(self) -> int:
		if (platform == "linux" or platform == "linux2"):
			if self.interface == True:
				interfaces = self.handle_interfaces()
				for interface in range(len(interfaces)):
					print(f"{interface}. {interfaces[interface]}")

				try:
					interface_to_use_address = interfaces[int(input(": "))]

				except (IndexError, TypeError, ValueError):
					self.ip = "127.0.0.1"

				else:
					self.ip = interface_to_use_address


	def async_loop(self) -> None:
		self.config()


		self.initialize_server()


		while True:

			try:

				selected_socket = self.selector.select()
				for key, events in selected_socket:
					if key.fileobj is not self.server:
						key.data(key.fileobj)
					else:
						key.data(self.server)


				sleep(0.01)

			except KeyboardInterrupt as e:

				if selected_socket:
					for socket_to_close, events in selected_socket:
						self.break_pipe(socket_to_close.fileobj)
				print("\rserver downed")
				
				break


if __name__ == '__main__':

	argument_parser = argparse.ArgumentParser(description="tool to work with some protocols in internet")

	argument_parser.add_argument("-i", "--ip", type=str, default="127.0.0.1", help="ip")
	argument_parser.add_argument("-p", "--port", type=int, default=9876, help="port")
	argument_parser.add_argument("-d", "--hexdump", action="store_false", default=True, help="use hexdumper")
	argument_parser.add_argument("-b", "--buffer", type=int, default=8192, help="size of buffer")
	argument_parser.add_argument("-c", "--client", type=int, default=1, help="number of active clients")
	argument_parser.add_argument("-f", "--interface", action="store_true", default=False, help="process interfaces (for linux only)")
	argument_parser.add_argument("-r", "--proxy", action="store_true", default=False, help="set up proxy (edit in ./config/proxy.json)")
	argument_parser.add_argument("-R", "--reconfigure", action="store_true", default=False, help="reconfigure file ./config/default.json")
	argument_parser.add_argument("-s", "--secure", action="store_true", help="use secure connection (paramiko) or not")

	parsed_arguments = argument_parser.parse_args()

	server = Server(
		bind_ip=parsed_arguments.ip, bind_port=parsed_arguments.port, hex_dumper=parsed_arguments.hexdump, buffer_length=parsed_arguments.buffer,
		max_clients=parsed_arguments.client, interface=parsed_arguments.interface, proxy=parsed_arguments.proxy
		)

	server.async_loop()