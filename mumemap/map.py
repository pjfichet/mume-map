import os
import json
import logging
from queue import SimpleQueue
import heapq
from difflib import SequenceMatcher
from . import gui
from . import fmt
from . import log

logger = logging.getLogger(__name__)

terrain_cost = {
	"cavern": 0.75,
	"city": 0.75,
	"building": 0.75,
	"tunnel": 0.75,
	"road": 0.85,
	"field": 1.5,
	"brush": 1.8,
	"forest": 2.15,
	"hills": 2.45,
	"shallows": 2.45,
	"mountains": 2.8,
	"undefined": 30.0,
	"water": 50.0,
	"rapids": 60.0,
	"underwater": 100.0,
	"deathtrap": 1000.0,
}

player_tiles = (
	'cleric',
	'elf-dark',
	'elf-grey',
	'elf-light',
	'elf',
	'helf-dark',
	'helf-light',
	'orc',
	'troll',
	'warrior',
)

class Exit:
	def __init__(self):
		self._direction = ""
		self.vnum = None
		self.to = "undefined"
		self.exitFlags = ["exit", ]
		self.door = ""
		self.doorFlags = []

class Room:
	def __init__(self):
		self.vnum = "-1"
		self.serverid = "0"
		self.area = ""
		self.name = ""
		self.desc = ""
		self.dynadesc = ""
		self.note = ""
		self.terrain = "undefined"
		self.light = "undefined"
		self.align = "undefined"
		self.portable = "undefined"
		self.ridable = "undefined"
		self.sundeath = "undefined"
		self.label = ""
		self.avoid = False
		self.highlight = False
		self.mobFlags = ()
		self.loadFlags = ()
		self.ingredients = ()
		self.x = 0
		self.y = 0
		self.z = 0
		self.exits = {}

	def __lt__(self, room):
		# heapq.heappush should'nt attempt to sort rooms.
		return False

	def distance(self, room):
		return abs(room.x - self.x) + abs(room.y - self.y) + abs(room.z - self.z)


class Map:
	def __init__(self):
		self._gui_queue = SimpleQueue()
		self.window = gui.GuiThread(self)
		self.datafile = ''
		self.database = {}
		self.rooms = {}
		self.currentRoom = Room()
		self.currentPath = []
		self.labels = {}
		self.synced = False
		self.playerTile = 'helf-light'

	def log(self, filename='map.log', verbosity=2, redirectstderr=False):
		log.log(filename, verbosity, redirectstderr)

	def open(self, datafile):
		self.datafile = datafile
		self.load()
		self.window.start()

	def dump(self):
		serverids = 0
		for vnum, roomdict in self.database.items():
			if vnum == "schema_version":
				continue
			if roomdict['server_id'] == '0' and self.rooms[vnum].serverid != '0':
				roomdict['server_id'] = self.rooms[vnum].serverid
				serverids += 1
				roomdict['name'] = self.rooms[vnum].name
				roomdict['description'] = self.rooms[vnum].desc
		if serverids > 0:
			logger.info(f"Added {serverids} server_id to map.")
			self.echo(f"Added {serverids} server_id to map.")
		data = json.dumps(self.database, sort_keys=True, indent=2)
		with open(self.datafile, "w") as f:
			f.write(data)
		logger.info(f"Map written on {self.datafile}.")

	def load(self):
		if not os.path.exists(self.datafile):
			return f"Error: {mapfile} does not exist."
		elif os.path.isdir(self.datafile):
			return f"Error: {mapfile} is a directory, not a file."
		with open(self.datafile, "rb") as f:
			self.database = json.load(f)
		self.loadRooms()
		self.currentRoom = self.rooms["0"]

	def loadRooms(self):
		serverids = 0
		for vnum, roomdict in self.database.items():
			if vnum == "schema_version":
				continue
			newroom = Room()
			newroom.vnum = vnum
			newroom.serverid = roomdict["server_id"]
			newroom.align = roomdict["alignment"]
			newroom.avoid = roomdict["avoid"]
			newroom.desc = roomdict["description"]
			newroom.dynadesc = roomdict["contents"].lstrip()
			newroom.light = roomdict["light"]
			newroom.loadFlags = set(roomdict["load_flags"])
			newroom.mobFlags = set(roomdict["mob_flags"])
			newroom.ingredients = set(roomdict["ingredients"])
			newroom.name = roomdict["name"]
			newroom.note = roomdict["note"]
			newroom.label = roomdict["label"]
			self.labels[newroom.label] = vnum
			newroom.portable = roomdict["portable"]
			newroom.rideable = roomdict["ridable"]
			newroom.sundeath = roomdict["sundeath"]
			newroom.terrain = roomdict["terrain"]
			newroom.cost = terrain_cost[newroom.terrain]
			if newroom.avoid:
				newroom.cost += 1000.0
			newroom.coordinates = roomdict["coordinates"]
			newroom.x = newroom.coordinates[0]
			newroom.y = newroom.coordinates[1]
			newroom.z = newroom.coordinates[2]
			newroom.area = roomdict["area"]
			for direction, exitdict in roomdict["exits"].items():
				newexit = Exit()
				newexit.direction = direction
				newexit.to = exitdict["to"]
				if vnum:
					newexit.vnum = vnum
				else:
					newexit.vnum = self.currentRoom.vnum
				newexit.door = exitdict["door"]
				newexit.doorFlags = list(exitdict["door_flags"])
				newexit.exitFlags = list(exitdict["exit_flags"])
				newroom.exits[direction] = newexit
				#exitdict.clear()
			if newroom.serverid != '0':
				serverids += 1
			self.rooms[vnum] = newroom
			# roomdict.clear()
		logger.info(f"Loaded {len(self.rooms)} rooms containing {serverids} server_id.")

	def getNeighbors(self, x, y, z, radius):
		"""A generator which yields all rooms in the vicinity of a room object.
		Each yielded result contains the vnum, room object reference, and difference in X-Y-Z coordinates."""
		radiusX, radiusY, radiusZ = radius
		for vnum, obj in self.rooms.items():
			differenceX, differenceY, differenceZ = obj.x - x, obj.y - y, obj.z - z
			if (
				abs(differenceX) <= radiusX
				and abs(differenceY) <= radiusY
				and abs(differenceZ) <= radiusZ
			):
				yield (vnum, obj, differenceX, differenceY, differenceZ)
				
	def move(self, direction, serverid, name, desc):
		if not direction and not serverid and not name:
			return
		logger.debug(f"Movement \"{direction}\" to room \"{name}\", \"{serverid}\".")
		if self.synced == True and direction:
			if direction in self.currentRoom.exits:
				logger.debug(f"Direction {direction} found in room {self.currentRoom.vnum}.")
				self.sync(self.rooms[self.currentRoom.exits[direction].to])
				self.match(serverid, name, desc)
				return
			else:
				self.synced = False
				logger.warning(f"Direction \"{direction}\" not found in room {self.currentRoom.vnum}.")
		# Move not found, make an extensive search:
		self.room(serverid, name, desc)

	def room(self, serverid, name, desc):
		if not name or not desc:
			return
		logger.debug(f"Searching for room \"{name}\", \"{serverid}\".")
		name = fmt.stringAscii(name)
		desc = fmt.stringAscii(desc)
		descRooms = []
		nameRooms = []
		for vnum, room in self.rooms.items():
			if serverid and room.serverid == serverid:
				logger.debug(f"Found room {room.vnum} by serverid.")
				self.sync(room)
				return
			if desc and room.desc == desc:
				descRooms.append(room)
			if name and room.name == name:
				nameRooms.append(room)
		if len(descRooms) == 1:
			logger.debug(f"Found room {descRooms[0].vnum} by desc.")
			self.sync(descRooms[0])
			self.match(serverid, name, desc)
			return
		elif len(nameRooms) == 1:
			logger.debug(f"Found room {nameRooms[0].vnum} by name only.")
			self.sync(nameRooms[0])
			self.match(serverid, name, desc)
			return
		self.synced = False
		self.echo("Room not found.")
		logger.warning(f"Room not found: (\"{serverid}\", \"{name}\", \"\"\"{desc}\"\"\")")

	def match(self, serverid, name, desc):
		logger.debug(f"Test if room {self.currentRoom.vnum} matches \"{name}\", \"{serverid}\".")
		if (serverid == '0' or serverid == ''
			or not name or not desc):
			return
		if  self.currentRoom.serverid == serverid:
			logger.debug(f"Room {self.currentRoom.vnum} has yet serverid {serverid}.")
			return
		name = fmt.stringAscii(name)
		desc = fmt.stringAscii(desc)
		if self.currentRoom.name == name and self.currentRoom.desc == desc:
			self.currentRoom.serverid = serverid
			self.synced = True
			logger.info(f"Exact match: add serverid {serverid} to room {self.currentRoom.vnum}.")
			return
		# exact match failed, try a partial match
		nameratio = SequenceMatcher(None, self.currentRoom.name.lower(), name.lower()).ratio()
		descratio = SequenceMatcher(None, self.currentRoom.desc.lower(), desc.lower()).ratio()			
		if nameratio >= 0.9 and descratio >= 0.8:
			self.currentRoom.serverid = serverid
			self.currentRoom.name = name
			self.currentRoom.desc = desc
			self.synced = True
			logger.info(f"Partial match (name: {nameratio}, desc: {descratio}): add serverid {serverid} to room {self.currentRoom.vnum}.")
			return
		else:
			logger.warning(f"Partial match failed (name: {nameratio}, desc: {descratio}).")
		# nothing matches
		logger.warning(f"Current room {self.currentRoom.vnum} does not match \"{serverid}\", \"{name}\", \"{desc}\".")
		self.synced = False
		#if self.currentRoom.serverid and self.currentRoom.serverid != '0':
			# we delete the wrong serverid
			#logger.warning(f"Deleting wrong serverid {self.currentRoom.serverid} from room {self.currentRoom.vnum}.")
			#self.currentRoom.serverid = '0'

	def sync(self, room):
		self.synced = True
		self.currentRoom = room
		self.info()
		self._gui_queue.put(("on_mapSync", self.currentRoom))
		logger.info(f"Synced to room {self.currentRoom.vnum}")

	def info(self):
		hidden = None
		deathtrap = None
		for direction, ex in self.currentRoom.exits.items():
			if self.currentRoom.exits[direction].to == 'death':
				if deathtrap == None:
					deathtrap = "Deathtrap: "
				else:
					deathtrap += ", "
				if self.currentRoom.exits[direction].door == '':
					deathtrap += direction
				else:
					deathtrap += f"'{ex.door}' {direction}"
			if 'hidden' in ex.doorFlags:
				if hidden == None:
					hidden = "Hidden: "
				else:
					hidden += ", "
				if self.currentRoom.exits[direction].door == '':
					hidden += f"{direction}"
				else:
					hidden += f"'{ex.door}' {direction}"
		if hidden:
			self.echo(hidden)
		if deathtrap:
			self.echo(deathtrap)
		if self.currentRoom.label:
			self.echo(f"Label: {self.currentRoom.label}")
		if self.currentRoom.note:
			self.echo(f"Note: {self.currentRoom.note}")

	def path(self, label):
		if not label:
			self.currentPath = []
		if label in self.labels:
			self._path(self.currentRoom, self.rooms[self.labels[label]])
		else:
			self.echo(f"Label {label} not found.")
			self.currentPath = []

	def _path(self, origin, destination):
		logger.info(f"Searching path from {origin.vnum} to {destination.vnum}.")
		self.currentPath = []
		parents = {origin: origin}
		#unprocessed and processed rooms:
		opened = []
		# use a binary heap to improve performances
		heapq.heapify(opened)
		heapq.heappush(opened, (origin.cost, origin))
		#opened.append((origin.cost, origin))
		closed = {}
		closed[origin] = origin.cost
		while opened:
			cost, room = heapq.heappop(opened)
			#cost, room = opened.pop()
			if room is destination:
				break
			for dir, exit in room.exits.items():
				if exit.to == 'death' or exit.to == 'undefined':
					continue
				neighbor = self.rooms[exit.to]
				neighborcost = cost + neighbor.cost
				if neighbor not in closed or closed[neighbor] > neighborcost:
					closed[neighbor] = neighborcost
					heapq.heappush(opened, (neighborcost, neighbor))
					#opened.append((neighborcost, neighbor))
					parents[neighbor] = room
		else:
			logger.warning("Path not found.")
			self.echo("Path not found.")
			return []
		result = []
		while room is not origin:
			room = parents[room]
			room.highlight = True
			self.currentPath.append(room)
		logger.info("Path found.")
		self.echo("Path found.")
		self._gui_queue.put(("on_mapSync", self.currentRoom))
		
	def findLabel(self, string):
		for label in self.labels:
			if string in label:
				self.echo(f"Room {self.rooms[self.labels[label]].vnum}: {label} ")

	def findNote(self, string):
		for vnum, room in self.rooms.items():
			if ingredient in room.note:
				room.highlight = True
				result.append(room)
		if not result:
			self.echo(f"Nothing found.")
			return
		result.sort(key=lambda x: x.distance(self.currentRoom))
		for room in result[:10]:
			self.echo(f"Room {room.vnum} ({room.distance(self.currentRoom)}): {room.note}")
		self._gui_queue.put(("on_mapSync", self.currentRoom))


	def findVnum(self, vnum):
		if vnum in self.rooms:
			room = self.rooms[vnum]
			if room.label:
				self.echo(f"Room {vnum}: {room.name} ({room.x},{room.y},{room.z} - {room.label}")
			else:
				self.echo(f"Room {vnum}: {room.name} ({room.x},{room.y},{room.z}")
			if room.note:
				self.echo(f"Room {vnum}: {room.note}")

	def findIngredient(self, ingredient):
		result = []
		for vnum, room in self.rooms.items():
			if ingredient in room.ingredients:
				room.highlight = True
				result.append(room)
		if not result:
			self.echo(f"Nothing found.")
			return
		result.sort(key=lambda x: x.distance(self.currentRoom))
		for room in result[:10]:
			self.echo(f"Room {room.vnum} ({room.distance(self.currentRoom)}): {", ".join(room.ingredients)}")
		self._gui_queue.put(("on_mapSync", self.currentRoom))


	def player(self, tile):
		if tile in player_tile:
			self.playerTile = tile
			self._gui_queue.put(("on_mapSync", self.currentRoom))
		else:
			self.echo(f"Player can be: {', '.join(player_tile)}.")

	def echo(self, message):
		print(f"map: {message}")

	def close(self):
		self._gui_queue.put(("on_close",))
		self.dump()
		logger.info("Closing map.")
