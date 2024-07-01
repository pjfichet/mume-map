ASCIIBOX = {
	"n": "╨",
	"e": "╞",
	"s": "╥",
	"w": "╡",
	"nesw": "╬",
	"ne": "╚",
	"esw": "╦",
	"ew": "═",
	"ns": "║",
	"es": "╔",
	"sw": "╗",
	"nw": "╝",
	"nes": "╠",
	"nsw": "╣",
	"esw": "╦",
	"new": "╩",
	"": "□",
}

		# list of ascii rooms
		self.ascii = {}
	
		self.draw_ascii(self.mcol, self.mrow, centerRoom)

				self.draw_ascii(self.mcol + x, self.mrow + y, room)

		self.print_ascii()

	def draw_ascii(self, x, y, room):
		char = ""
		for direction in ("north", "east", "south", "west"):
			if direction in room.exits:
				char += direction[0]
		self.ascii[x, y] = char

	def print_ascii(self):
		map = ""
		for y in range(self.mrow + 5, self.mrow -5, -1):
			for x in range(self.mcol -10, self.mcol +10):
				if (x, y) in self.ascii:
					if self.ascii[x, y] not in ASCIIBOX:
						print(self.ascii[x, y])
					else:
						map += ASCIIBOX[self.ascii[x, y]]
				else:
					map += " "
			map += "\n"
		print(map)
			


