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
			cmd = cmd.split(' ')
			if cmd[0] == 'k':
				self.direction('north')
			elif cmd[0] == 'h':
				self.direction('west')
			elif cmd[0] == 'j':
				self.direction('south')
			elif cmd[0] == 'l':
				self.direction('east')
			elif cmd[0] == 'u':
				self.direction('up')
			elif cmd[0] == 'n':
				self.direction('down')
			elif cmd[0].isdigit():
				self.vnum(cmd[0])
			elif cmd[0] == 'label' and len(cmd) > 1:
				self.map.findLabel(cmd[1])
			elif cmd[0] == 'ingredient' and len(cmd) > 1:
				self.map.findIngredient(cmd[1])
			elif cmd[0] == 'path' and len(cmd) > 1:
				self.map.path(cmd[1])
			elif cmd[0] == 'player' and len(cmd) > 1:
				self.map.player(cmd[1])
			elif cmd[0] == 'quit' or cmd[0] == 'q':
				break
		# after loop break
		print("Goodbye.")
		self.map.close()
