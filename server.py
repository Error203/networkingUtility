import socket
import hex_dump
from time import sleep
import selectors
import argparse
from netifaces import interfaces, ifaddresses, AF_INET


class Server:


	def __init__(self, bind_ip: str="127.0.0.1", bind_port: int=9876, buffer_length: int=8192, hex_dumper: bool=True) -> object:
		print("\rinitializng...")
		self.ip = bind_ip
		self.port = bind_port
		self.buffer_length = buffer_length
		self.hex_dumper = hex_dumper
		self.argument_parser = argparse.ArgumentParser()

		selector = selectors.DefaultSelector()
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server.bind((self.ip, self.port))
		server.listen(2)
		selector.register(fileobj=server, events=selectors.EVENT_READ, data=self.accept_connection)

		self.server = server
		self.selector = selector

		if hex_dumper:
			self.hex_dump = hex_dump.Hex(show=self.hex_dumper).hex_dump

		print("searching interfaces...")

		for ifaceName in interfaces():
			addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
			print(' '.join(addresses))


	def send_data(self, data: bytes, client_endpoint: socket.socket) -> int:
		if not isinstance(data, bytes):
			data = data.encode("utf-8")

		data += b"\r\n"

		print("\rsending...")

		client_endpoint.send(data)

		return 1


	def receive_data(self, client_endpoint: socket.socket) -> bytes:
		data_buffer = b""
		client_endpnt = client_endpoint.getpeername()

		print(f"\rreceiving...{client_endpnt[0]}:{client_endpnt[1]}")

		data_buffer += client_endpoint.recv(self.buffer_length)

		if self.hex_dumper:
			self.hex_dump(data_buffer)

		if not data_buffer:
			self.break_pipe(client_endpoint)
			self.selector.unregister(client_endpoint)
		
		return data_buffer


	def break_pipe(self, socket: socket.socket) -> None:
		client_endpnt = socket.getpeername()
		if socket.fileno() != -1:
			print(f"\rclosing socket...{client_endpnt[0]}:{client_endpnt[1]}")
			socket.close()

		print(f"\rcleaning up...{client_endpnt[0]}:{client_endpnt[1]}")


	def accept_connection(self) -> None:
		print("\rlistening...")
		client, address_info = self.server.accept()
		print("client: %s:%d" % (address_info[0], address_info[1]))

		self.selector.register(fileobj=client, events=selectors.EVENT_READ, data=self.receive_data)


	def async_loop(self) -> None:

		while True:

			selected_socket = self.selector.select()
			for key, events in selected_socket:
				if key.fileobj is not self.server:
					key.data(key.fileobj)
				else:
					key.data()


			sleep(0.01)


if __name__ == '__main__':
	server = Server(hex_dumper=True)
	server.async_loop()