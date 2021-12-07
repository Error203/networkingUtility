#!/bin/bash

class Hex:


	def __init__(self, show: bool=False) -> object:
		self.show = show


	def hex_dump(self, source: [bytes, str], length: int=16) -> str:
			hex_filter = "".join([(len(repr(chr(i))) == 3) and chr(i) or "." for i in range(256)])

			if isinstance(source, bytes):
				source = source.decode("utf-8")

			results = list()
			for i in range(0, len(source), length):
				word = str(source[i:i + length])

				to_print = word.translate(hex_filter)
				hexa = " ".join([f"{ord(char):02x}" for char in word])
				hex_width = length * 3
				results.append(f"{i:04x} {hexa:<{hex_width}} {to_print}")

			if self.show:
				for line in results:
					print(line)

			return results