from qlogger import Logger
import argparse
import socket


class WebDog:


	def __init__(self, args):
		self.log = Logger("WebDog Logs").get_logger("WebDog")
		self.args = args

		if not self.args.ip:
			self.ip = "192.168.0.100"
			self.log.warning("ip is not set. (default: 192.168.0.100)")
		
		if not self.args.port:
			self.port = 9873
			self.log.warning("port is not set. (default: 9873)")


	def listen(self):
		try:
			self.tcp_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.tcp_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.tcp_listener.bind((self.ip, self.port))
			self.tcp_listener.listen(1)
			self.log.info(f"tcp listener set up {self.ip}:{self.port}")
			self.client, address_info = self.tcp_listener.accept()
			self.log.info(f"caught up connection {address_info[0]}:{address_info[1]}")

		except Exception as e:
			self.log.exception(e)
			self.break_pipe(self.tcp_listener)

			exit(0)

		except (KeyboardInterrupt, EOFError):
			self.break_pipe(self.tcp_listener)
			
			exit(1)


	def communicate(self):
		try:
			self.communicator = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.communicator.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.communicator.connect((self.ip, self.port))
			self.log.info(f"connected to {self.ip}:{self.port}")

		except Exception as e:
			self.log.exception(e)
			self.break_pipe(self.communicator)

			exit(0)

		except (KeyboardInterrupt, EOFError):
			self.break_pipe(self.communicator)
			
			exit(1)


	def chat(self, interlocutor_nickname="interlocutor"):
		try:
			self.nickname = str(input("enter nickname: "))
			if not self.nickname:
				self.nickname = "anonymous"

			if self.args.listen:
				self.log.info("waiting for header")
				self.header_page = self.client.recv(4096).decode("utf-8")
				self.header_page = self.header_page.strip().replace(" ", "").split(";")
				self.log.info("got header page")
				if self.header_page[0] == "DEST.NICKNAME":
					self.interlocutor_nickname = str(self.header_page[1])
				self.header_page = f"DEST.NICKNAME;{self.nickname}".encode("utf-8")
				self.client.send(self.header_page)
				self.log.info("sent header page")

			else:
				self.header_page = f"DEST.NICKNAME;{self.nickname}".encode("utf-8")
				self.communicator.send(self.header_page)
				self.log.info("sent header page")
				self.log.info("waiting for header")
				self.header_page = self.communicator.recv(4096).decode("utf-8")
				self.header_page = self.header_page.strip().replace(" ", "").split(";")
				self.log.info("got header page")
				if self.header_page[0] == "DEST.NICKNAME":
					self.interlocutor_nickname = str(self.header_page[1])

			while True:
				if self.args.listen:
					print(f"{self.interlocutor_nickname} says: ", end="")
					message = b""

					while True:
						message += self.client.recv(4096).decode("utf-8")
						if len(message) < 4096:
							break

					print(message)

					buffer = str(input("you: ")).encode("utf-8")
					self.client.send(buffer)

				else:
					buffer = str(input("you: ")).encode("utf-8")
					self.communicator.send(buffer)

					print(f"{self.interlocutor_nickname} says: ", end="")
					message = b""

					while True:
						message += self.communicator.recv(4096).decode("utf-8")
						if len(message) < 4096:
							break

					print(message)

		except Exception as e:
			self.log.exception(e)
			self.break_pipe(self.communicator)
			self.break_pipe(self.tcp_listener)

			exit(0)

		except KeyboardInterrupt:
			self.log.info("got stop signal")
			self.break_pipe(self.communicator)
			self.break_pipe(self.tcp_listener)

			exit(1)


	def break_pipe(self, socket_object):
		if socket_object.fileno() == "-1":
			self.log.warning("connection was broken by another process")

		elif socket_object.fileno() != "-1":
			socket_object.close()
			del(socket_object)
			self.log.info("cleaned connection up")


if __name__ == '__main__':
	try:
		root_logger = Logger().get_logger("ROOT")

		parser = argparse.ArgumentParser(
			description="WebDog webwork* tool. (netcat analog).",
			epilog="Simple use. Can be used without arguments.",
			)
		parser.add_argument("--ip", type=str, default=None, help="specify an ip address to connect or to listen to.")
		parser.add_argument("--port", type=int, default=None, help="specify a port to connect or to listen to.")
		parser.add_argument("-l", "--listen", action="store_true", help="add this key to listen first (be a server).")
		args = parser.parse_args()

		wd = WebDog(args)
		if args.listen:
			wd.listen()
		else:
			wd.communicate()

		chat()

	except Exception as e:
		exit(0)