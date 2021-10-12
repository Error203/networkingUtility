import qlogger
import argparse
import server
import os


class WebDog:
	def __init__(self):
		parser = argparse.ArgumentParser(
					description="WebDog network tool. (netcat analog).",
					epilog="Simple use. Can be used without arguments.",
					)
		parser.add_argument("--ip", type=str, default="192.168.0.100", help="specify an ip address to connect or to listen to.")
		parser.add_argument("--port", type=int, default=9876, help="specify a port to connect or to listen to.")
		parser.add_argument("-l", "--listen", action="store_true", help="add this key to listen first (be a server).")
		parser.add_argument("-v", "--verbose", action="store_true", help="more detailed information about webdog steps.")

		self.args = parser.parse_args()

		if self.args.verbose:
			self.log_level = qlogger.logging.DEBUG
		else:
			self.log_level = qlogger.logging.INFO

		self.log = qlogger.Logger(os.path.join("logs", "webdog log"), self.log_level).get_logger("webdog")

		self.ip = self.args.ip
		self.port = self.args.port


	def termux_sensor(self, socket, its_role):
		pass
		# if its_role == "server":
		# 	command_to_execute = "termux-sensor -s \"LSM6DSL Gyroscope\""
		# 	socket.send_data(os.system(command_to_execute))
		# elif its_role == "client":
		# 	socket.receive_data()


	def main_loop(self):
		if self.args.listen:
			try:
				import server
				_server = server.Server(self.ip, self.port, self.log_level)
				_server.start_server()
				self.log.info("imported module: server")
				_server.console_client()
				# _server.chatting_room()
				# termux_sensor(_server, "server")
				# _server.send_file("українська.txt")

			except Exception as e:
				self.log.exception(e)

			finally:
				_server.break_pipe()

		else:
			try:
				import client
				_client = client.Client(self.ip, self.port, self.log_level)
				_client.start_client()
				self.log.info("imported module: client")
				_client.console_host()
				# _client.chatting_room()
				# termux_sensor(_client, "client")
				# _client.receive_file()

			except Exception as e:
				self.log.exception(e)

			finally:
				_client.break_pipe()


if __name__ == '__main__':
	wd = WebDog()
	wd.main_loop()
