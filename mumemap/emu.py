from .map import Map

class Emulation:
	def __init__(self):
		self.map = Map()

	def log(self, filename, verbosity, redirectstderr):
		self.map.log(filename, verbosity, redirectstderr)

	def direction(self, direction):
		if direction in self.map.currentRoom.exits:
			self.room(self.map.rooms[self.map.currentRoom.exits[direction].to])

	def vnum(self, vnum):
		if vnum in self.map.rooms:
			self.room(self.map.rooms[vnum])

	def room(self, room):
		self.map.currentRoom = room
		print(f"\x1b[0;32m{room.x} {room.y}, {room.z}: {room.name}\x1b[0m")
		print(self.map.currentRoom.desc)
		print(self.map.currentRoom.dynadesc)
		self.map.sync(self.map.currentRoom)

	def run(self, datafile):
		print("Hello Middle Earth !")
		self.map.open(datafile)
		self.vnum('17903') # moria east gate
		while True:
			cmd = input("> ")
			if cmd == 'k':
				self.direction('north')
			elif cmd == 'h':
				self.direction('west')
			elif cmd == 'j':
				self.direction('south')
			elif cmd == 'l':
				self.direction('east')
			elif cmd == 'u':
				self.direction('up')
			elif cmd == 'n':
				self.direction('down')
			elif cmd.isdigit():
				self.vnum(cmd)
			elif cmd.split(' ')[0] == 'label':
				self.map.findLabel(cmd[1])
			elif cmd == 'quit' or cmd == 'q':
				break
		# after loop break
		print("Goodbye.")
		self.map.close()
