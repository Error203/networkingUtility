# coding: utf-8

import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading


def execute(cmd):
	cmd = cmd.strip() # remove useless spaces
	if not cmd:
		return
	output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT, shell=True)
	return output.decode()


class WebDog:


	def __init__(self, args, buffer=None):
		self.args = args
		self.buffer = buffer
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


	def run(self):
		if self.args.listen:
			self.listen()
		else:
			self.send()


	def send(self):
		self.socket.connect((self.args.target, self.args.port))
		if self.buffer:
			self.socket.send(self.buffer)

		try:
			while True:
				recv_len = 1
				response = ""
				while recv_len:
					data = self.socket.recv(4096)
					recv_len = len(data)
					response += data.decode()
					if recv_len < 4096:
						break
				if response:
					print(response)
					buffer = input(">")
					buffer += "\n"
					self.socket.send(buffer.encode())
		except KeyboardInterrupt:
			self.socket.close()
			sys.exit()


	def listen(self):
		self.socket.bind((self.args.target, self.args.port))
		self.socket.listen(5)
		while True:
			client_socket, _ = self.socket.accept()
			client_thread = threading.Thread(target=self.handle, args=(client_socket,))
			client_thread.start()


	def handle(self, client_socket):
		if self.args.execute:
			output = execute(self.args.execute)
			client_socket.send(output.encode())

		elif self.args.upload:
			file_buffer = b""
			while True:
				data = client_socket.recv(4096)
				if data:
					file_buffer += data
				else:
					break

			with open(self.args.upload, "wb") as f:
				f.write(file_buffer)
			message = f"saved file {self.args.upload}"
			client_socket.send(message.encode())

		elif self.args.command:
			cmd_buffer = b""
			while True:
				try:
					client_socket.send(b"$ ")
					while "\n" not in cmd_buffer.decode():
						cmd_buffer += client_socket.recv(64)
					response = execute(cmd_buffer.decode())
					if response:
						client_socket.send(response.encode())
					cmd_buffer = b""
				except Exception as e:
					print(e)
					self.socket.close()
					sys.exit()


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description="WebDog webworking utility. (netcat analog)",
		formatter_class=argparse.RawTextHelpFormatter,
		epilog=textwrap.dedent("""Simple use.
			webdog.py --target 192.168.0.100 --port 5555 -lc
		"""))

	parser.add_argument("-c", "--command", action="store_true", help="set up a command shell between machines.")
	parser.add_argument("-e", "--execute", help="execute command once and return output. no deadless connection.")
	parser.add_argument("-l", "--listen", action="store_true", help="listen for incoming.")
	parser.add_argument("--port", type=int, help="specify port to connect or to listen to.")
	parser.add_argument("--target", help="specify ip to connect or to listen to.")
	parser.add_argument("-u", "--upload", help="upload file to machine.")
	args = parser.parse_args()
	if args.listen:
		buffer = ""
	else:
		buffer = sys.stdin.read()

	wd = WebDog(args, buffer.encode())
	wd.run()