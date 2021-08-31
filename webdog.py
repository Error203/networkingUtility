import qlogger
import socket
import time
import argparse

class Server:
	# not AES-256 protected connection

	def __init__(self, ip, port):
		self.log = qlogger.Logger("server log", level=qlogger.logging.DEBUG).get_logger("server")
		self.ip = ip
		self.port = port

		self.log.debug("critical")


class Client:
	# not AES-256 protected connection

	def __init__(self, ip, port):
		self.log = qlogger.Logger("client log", level=qlogger.logging.DEBUG).get_logger("client")
		self.ip = ip
		self.port = port

		self.log.debug("client initialized")


	def empty(self):
		self.log.debug("debug")


if __name__ == '__main__':
	
	try:
		root_log = qlogger.Logger("root log", level=qlogger.logging.DEBUG).get_logger("root")

		parser = argparse.ArgumentParser(
			description="WebDog network tool. (netcat analog for Python compilers).",
			epilog="Simple use. Can be used without arguments.",
			)
		parser.add_argument("-i", "--ip", type=str, default="192.168.0.100", help="specify an ip address to connect or to listen to.")
		parser.add_argument("-p", "--port", type=int, default=9876, help="specify a port to connect or to listen to.")
		parser.add_argument("-l", "--listen", action="store_true", help="add this key to listen first (be a server).")
		args = parser.parse_args()

		if args.listen:
			server = Server(args.ip, args.port)
		else:
			client = Client(args.ip, args.port)
			client.empty()

	except Exception as e:
		root_log.exception(e)

		exit(1)

	else:
		root_log.info("modules imported successfully and loop worked correctly - 0")

		exit(0)