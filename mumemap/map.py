import os
import json
import logging
from queue import SimpleQueue
import heapq
from difflib import SequenceMatcher
import sys
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
		self.flags = []
		self.x = 0
		self.y = 0
		self.z = 0
		self.exits = {}

	def __lt__(self, room):
		# heapq.heappush should'nt attempt to sort rooms.
		return False

	def distance(self, room):
		return abs(room.x - self.x) + abs(room.y - self.y) + abs(room.z - self.z)

	def printExits(self):
		exits = None
		for direction, exit in self.exits.items():
			if exits:
				exits += ', '
			else:
				exits = "Exits: "
			if exit.door:
				exits += f"'{exit.door}' {direction}"
			else:
				exits += direction
			if exit.to == 'death' and 'hidden' in exit.doorFlags:
				exits += " (death, hidden)"
			elif exit.to == 'death':
				exits += " (death)"
			elif 'hidden' in exit.doorFlags:
				exits += " (hidden)"
		return(exits)


class Map:
	def __init__(self):
		self._gui_queue = SimpleQueue()
		self.window = gui.GuiThread(self)
		self.mapfile = ''
		self.labelfile = ''
		self.database = {}
		self.rooms = {}
		self.currentRoom = Room()
		self.currentPath = []
		self.labels = {}
		self.labelled = {} # invert of self.labels
		self.synced = False
		self.playerTile = 'helf-light'

	def log(self, filename='map.log', verbosity=2, redirectstderr=False):
		log.log(filename, verbosity, redirectstderr)

	def open(self, mapfile, labelfile):
		# load labels first as loadRooms() need them.
		self.labelfile = labelfile
		self.labels = self.loadFile(labelfile)['labels']
		self.labelled = {value: key for key, value in self.labels.items()}
		self.mapfile = mapfile
		self.database = self.loadFile(mapfile)
		self.loadRooms()
		self.currentRoom = self.rooms["0"]
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
		with open(self.mapfile, "w") as f:
			f.write(data)
		logger.info(f"Map written on {self.mapfile}.")

	def loadFile(self, jsonfile):
		if not os.path.exists(jsonfile):
			sys.exit(f"Error: {jsonfile} does not exist.")
		elif os.path.isdir(jsonfile):
			sys.exit(f"Error: {jsonfile} is a directory, not a file.")
		with open(jsonfile, "rb") as f:
			return json.load(f)

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
			newroom.flags += roomdict["load_flags"]
			newroom.flags += roomdict["mob_flags"]
			newroom.flags += roomdict["ingredient_flags"]
			newroom.name = roomdict["name"]
			newroom.note = roomdict["note"]
			if vnum in self.labelled:
				newroom.label = self.labelled[vnum]
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
		"""Synchronize by movement direction."""
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
		"""Synchronize by room content (serverid, name, description)"""
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
		"""Add server_id to room if it matches correctly"""
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
		# nothing matches
		logger.warning(f"Partial match failed (name: {nameratio}, desc: {descratio}).")
		logger.warning(f"Current room {self.currentRoom.vnum} does not match \"{serverid}\", \"{name}\", \"{desc}\".")
		self.synced = False
		#if self.currentRoom.serverid and self.currentRoom.serverid != '0':
			# we delete the wrong serverid
			#logger.warning(f"Deleting wrong serverid {self.currentRoom.serverid} from room {self.currentRoom.vnum}.")
			#self.currentRoom.serverid = '0'

	def diff(self, name, desc, json_exits):
		"""Calculates the diff between mume room and map room"""
		logger.debug(f"Calculate diff of {self.currentRoom.vnum} with server info.")
		exits = json.loads(json_exits[0:-2])
		name = fmt.stringAscii(name)
		desc = fmt.stringAscii(desc)
		if self.currentRoom.name == name:
			nameratio = 1
		else:
			nameratio = SequenceMatcher(None, self.currentRoom.name.lower(), name.lower()).ratio()
			self.echo(f"map:{self.currentRoom.name}")
			self.echo(f"mum:{name}")
		if self.currentRoom.desc == desc:
			descratio = 1
		else:
			descratio = SequenceMatcher(None, self.currentRoom.desc.lower(), desc.lower()).ratio()
			self.echo(f"map:{self.currentRoom.desc}")
			self.echo(f"mum:{desc}")
		exitmore = []
		exitless = []
		for exit in ["north", "east", "south", "west", "up", "down"]:
			if exit in self.currentRoom.exits and exit[0] not in exits:
				exitmore.append(exit)
			if exit not in self.currentRoom.exits and exit[0] in exits:
				exitless.append(exit)
		self.echo(f"Diff of {self.currentRoom.vnum}, name:{nameratio:.2f}, desc:{descratio:.2f}, more:{exitmore}, less:{exitless}")

	def copy(self, serverid, name, desc):
		self.currentRoom.serverid = serverid
		self.currentRoom.name = fmt.stringAscii(name)
		self.currentRoom.desc = fmt.stringAscii(desc)
		self.synced = True
		self.echo(f"Room {self.currentRoom.vnum} overwritten.")
		logger.info(f"Overwriting room {self.currentRoom.vnum} with server data.")

	def sync(self, room):
		self.synced = True
		self.currentRoom = room
		self.info()
		self._gui_queue.put(("on_mapSync", self.currentRoom))
		logger.debug(f"Synced to room {self.currentRoom.vnum}")

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

	def path(self, dest):
		if not dest:
			self.currentPath = []
			self.unhighlight()
		elif dest in self.labels:
			self._path(self.currentRoom, self.rooms[self.labels[dest]])
		elif dest in self.rooms:
			self._path(self.currentRoom, self.rooms[dest])
		else:
			self.echo(f"Room {dest} not found.")
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

	def unhighlight(self):
		for vnum, room in self.rooms.items():
			room.highlight = False
		self._gui_queue.put(("on_mapSync", self.currentRoom))

	def infoRoom(self, vnum=None):
		if not vnum:
			room = self.currentRoom
			vnum = self.currentRoom.vnum
		elif vnum in self.rooms:
			room = self.rooms[vnum]
		else:
			self.echo(f"Room {vnum} not found.")
			return
		self.echo(f"{vnum}: {room.name} ({room.label})")
		self.echo(f"{vnum}: {room.printExits()}")
		self.echo(f"{vnum}: {", ".join(room.flags)}")
		self.echo(f"{vnum}: {room.note}")

	def findRoom(self, value):
		result = []
		for label in self.labels:
			if value in label:
				result.append((self.rooms[self.labels[label]], 'label'))
		for vnum, room in self.rooms.items():
			if value in room.name.lower():
				result.append((room, 'name'))
			if value in room.note.lower():
				result.append((room, 'note'))
			if value in room.flags:
				result.append((room, 'flags'))
		if not result:
			self.echo(f"Nothing found.")
			return
		result.sort(key = lambda x: x[0].distance(self.currentRoom))
		for room, attribute in result[:10]:
			self.echo(f"Room {room.vnum} ({room.distance(self.currentRoom)}, {attribute}): {getattr(room, attribute)}")
		self._gui_queue.put(("on_mapSync", self.currentRoom))

	def player(self, tile):
		if tile in player_tiles:
			self.playerTile = tile
			self._gui_queue.put(("on_mapSync", self.currentRoom))
		else:
			self.echo(f"Player can be: {', '.join(player_tiles)}.")

	def echo(self, message):
		print(f"map: {message}")

	def close(self):
		self._gui_queue.put(("on_close",))
		self.dump()
		logger.info("Closing map.")
