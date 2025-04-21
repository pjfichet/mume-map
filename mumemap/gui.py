# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os.path
import re
import sys
from queue import Empty as QueueEmpty
import threading
import logging
logger = logging.getLogger(__name__)
#logger.setLevel(logging.WARNING)

# Third-party Modules:
import pyglet

pyglet.options["debug_gl"] = False
FPS = 40

d = os.path.dirname(sys.modules['mumemap'].__file__)
TILESDIR = os.path.join(d, 'tiles')

TILES = {
	# terrain
	"field": pyglet.image.load(os.path.join(TILESDIR, "field.png")),
	"brush": pyglet.image.load(os.path.join(TILESDIR, "brush.png")),
	"forest": pyglet.image.load(os.path.join(TILESDIR, "forest.png")),
	"hills": pyglet.image.load(os.path.join(TILESDIR, "hill.png")),
	"mountains": pyglet.image.load(os.path.join(TILESDIR, "mountain.png")),
	"shallows": pyglet.image.load(os.path.join(TILESDIR, "swamp.png")),
	"water": pyglet.image.load(os.path.join(TILESDIR, "water.png")),
	"rapids": pyglet.image.load(os.path.join(TILESDIR, "rapid.png")),
	"underwater": pyglet.image.load(os.path.join(TILESDIR, "underwater.png")),
	"cavern": pyglet.image.load(os.path.join(TILESDIR, "cavern.png")),
	"tunnel": pyglet.image.load(os.path.join(TILESDIR, "tunnel.png")),
	"road": pyglet.image.load(os.path.join(TILESDIR, "road.png")),
	"city": pyglet.image.load(os.path.join(TILESDIR, "city.png")),
	"building": pyglet.image.load(os.path.join(TILESDIR, "indoor.png")),
	"random": pyglet.image.load(os.path.join(TILESDIR, "random.png")),
	"undefined": pyglet.image.load(os.path.join(TILESDIR, "undefined.png")),
	"deathtrap": pyglet.image.load(os.path.join(TILESDIR, "undefined.png")),
	# dark terrain
	"field-dark": pyglet.image.load(os.path.join(TILESDIR, "field-dark.png")),
	"brush-dark": pyglet.image.load(os.path.join(TILESDIR, "brush-dark.png")),
	"forest-dark": pyglet.image.load(os.path.join(TILESDIR, "forest-dark.png")),
	"hills-dark": pyglet.image.load(os.path.join(TILESDIR, "hill-dark.png")),
	"mountains-dark": pyglet.image.load(os.path.join(TILESDIR, "mountain-dark.png")),
	"shallows-dark": pyglet.image.load(os.path.join(TILESDIR, "swamp-dark.png")),
	"water-dark": pyglet.image.load(os.path.join(TILESDIR, "water-dark.png")),
	"rapids-dark": pyglet.image.load(os.path.join(TILESDIR, "rapid-dark.png")),
	"underwater-dark": pyglet.image.load(os.path.join(TILESDIR, "underwater-dark.png")),
	"cavern-dark": pyglet.image.load(os.path.join(TILESDIR, "cavern-dark.png")),
	"tunnel-dark": pyglet.image.load(os.path.join(TILESDIR, "tunnel-dark.png")),
	"road-dark": pyglet.image.load(os.path.join(TILESDIR, "road-dark.png")),
	"city-dark": pyglet.image.load(os.path.join(TILESDIR, "city-dark.png")),
	"building-dark": pyglet.image.load(os.path.join(TILESDIR, "indoor-dark.png")),
	"random-dark": pyglet.image.load(os.path.join(TILESDIR, "random-dark.png")),
	"undefined-dark": pyglet.image.load(os.path.join(TILESDIR, "undefined.png")),
	"deathtrap-dark": pyglet.image.load(os.path.join(TILESDIR, "undefined.png")),
	# exits
	"wallnorth": pyglet.image.load(os.path.join(TILESDIR, "wallnorth.png")),
	"walleast": pyglet.image.load(os.path.join(TILESDIR, "walleast.png")),
	"wallsouth": pyglet.image.load(os.path.join(TILESDIR, "wallsouth.png")),
	"wallwest": pyglet.image.load(os.path.join(TILESDIR, "wallwest.png")),
	"exitup": pyglet.image.load(os.path.join(TILESDIR, "exitup.png")),
	"exitdown": pyglet.image.load(os.path.join(TILESDIR, "exitdown.png")),
	# load flags
	"armour": pyglet.image.load(os.path.join(TILESDIR, "armour.png")),
	"herb": pyglet.image.load(os.path.join(TILESDIR, "herb.png")),
	"key": pyglet.image.load(os.path.join(TILESDIR, "key.png")),
	"treasure": pyglet.image.load(os.path.join(TILESDIR, "treasure.png")),
	"weapon": pyglet.image.load(os.path.join(TILESDIR, "weapon.png")),
	# mob flags
	"guild": pyglet.image.load(os.path.join(TILESDIR, "guild.png")),
	"quest_mob": pyglet.image.load(os.path.join(TILESDIR, "quest.png")),
	"rent": pyglet.image.load(os.path.join(TILESDIR, "rent.png")),
	"shop": pyglet.image.load(os.path.join(TILESDIR, "shop.png")),
	"aggressive_mob": pyglet.image.load(os.path.join(TILESDIR, "aggressive-mob.png")),
	"elite_mob": pyglet.image.load(os.path.join(TILESDIR, "elite-mob.png")),
	"super_mob": pyglet.image.load(os.path.join(TILESDIR, "super-mob.png")),
	# actually, attention flag is used for so many things it becomes meaningless
	"attention": pyglet.image.load(os.path.join(TILESDIR, "helmet.png")),
	# player
	"cleric": pyglet.image.load(os.path.join(TILESDIR, "cleric.png")),
	"elf-dark": pyglet.image.load(os.path.join(TILESDIR, "elf-dark.png")),
	"elf-grey": pyglet.image.load(os.path.join(TILESDIR, "elf-grey.png")),
	"elf-light": pyglet.image.load(os.path.join(TILESDIR, "elf-light.png")),
	"elf": pyglet.image.load(os.path.join(TILESDIR, "elf.png")),
	"helf-dark": pyglet.image.load(os.path.join(TILESDIR, "helf-dark.png")),
	"helf-light": pyglet.image.load(os.path.join(TILESDIR, "helf-light.png")),
	"orc": pyglet.image.load(os.path.join(TILESDIR, "orc.png")),
	"troll": pyglet.image.load(os.path.join(TILESDIR, "troll.png")),
	"warrior": pyglet.image.load(os.path.join(TILESDIR, "warrior.png")),

	# other
	"label": pyglet.image.load(os.path.join(TILESDIR, "label.png")),
	"noid": pyglet.image.load(os.path.join(TILESDIR, "noid.png")),
	"path": pyglet.image.load(os.path.join(TILESDIR, "path.png")),
}

# Ordered list of flags: only the first found is displayed.
# Since python 3.7 a dict must preserve its order.
DISPLAY_FLAGS = {
	# rent
	"rent": "rent",
	# guilds
	"guild": "guild",
	"scout_guild": "guild",
	"mage_guild": "guild",
	"cleric_guild": "guild",
	"warrior_guild": "guild",
	"ranger_guild": "guild",
	# shops
	"shop": "shop",
	"weapon_shop": "shop",
	"armour_shop": "shop",
	"food_shop": "shop",
	"pet_shop": "shop",
	# quests
	"quest_mob": "quest_mob",
	# danger
	"super_mob": "super_mob",
	"elite_mob": "elite_mob",
	"roots": "elite_mob",
	"rattlesnake": "elite_mob",
	"aggressive_mob": "aggressive_mob",
	# attention
	"attention": "attention",
	# load
	"treasure": "treasure",
	"key": "key",
	"armour": "armour",
	"weapon": "weapon",
	"herb": "herb",
}

class Window(pyglet.window.Window):  # type: ignore[misc, no-any-unimported]
	def __init__(self, world):
		# Mapperproxy world
		self.world = world
		# Map variables
		# Number of columns
		self.col: int = 9
		# Number of rows
		self.row: int = 23
		# The center of the window
		self.mcol: int = int(self.col / 2)
		self.mrow: int = int(self.row / 2)
		self.radius: tuple[int, int, int] = (self.mcol, self.mrow, 1)
		# The size of a tile in pixels
		self.square: int = 32
		# The list of visible rooms:
		# A dictionary using a tuple of coordinates (x, y) as keys
		self.visibleRooms = {}
		# Player position, set to None at startup.
		self.playerRoom = None
		# center coordinates
		self.cx = 0
		self.cy = 0
		self.cz = 0
		# room selected by right click
		self.selectedRoom = None
		# Pyglet window
		super().__init__(self.col * self.square, self.row * self.square, caption="Mumemap", resizable=True)
		logger.info(f"Creating window {self}")
		self._gui_queue = self.world._gui_queue
		# Sprites
		# The list of sprites
		self.sprites: list[SpriteType] = []
		# Pyglet batch of sprites
		self.batch: BatchType = pyglet.graphics.Batch()
		# The list of visible layers (level 0 is covered by level 1)
		self.layer: list[GroupType]
		self.layer = [pyglet.graphics.Group(order=i) for i in range(4)]
		# Define FPS
		pyglet.clock.schedule_interval_soft(self.queue_observer, 1.0 / FPS)

	def getWorldCoordinates(self, x, y):
		x = self.cx - self.mcol + x
		y = self.cy - self.mrow + y
		return(x, y)

	def queue_observer(self, dt: float) -> None:
		while not self._gui_queue.empty():
			#with suppress(QueueEmpty):
			try:
				event = self._gui_queue.get_nowait()
				if event is None:
					event = ("on_close",)
				self.dispatch_event(event[0], *event[1:])
			except QueueEmpty:
				pass

	def on_close(self) -> None:
		logger.info(f"Closing window {self}")
		super().on_close()

	def on_draw(self) -> None:
		logger.debug(f"Drawing window {self}")
		# pyglet stuff to clear the window
		self.clear()
		# pyglet stuff to print the batch of sprites
		self.batch.draw()

	def on_resize(self, width: int, height: int) -> None:
		logger.debug(f"Resizing window {self}")
		super().on_resize(width, height)
		# reset window size
		self.col = int(width / self.square)
		self.mcol = int(self.col / 2)
		self.row = int(height / self.square)
		self.mrow = int(self.row / 2)
		self.radius = (self.mcol, self.mrow, 1)
		self.draw_map(self.cx, self.cy, self.cz)

	def on_mapSync(self, currentRoom):
		logger.debug(f"Map synced to room {currentRoom.vnum}")
		# reset player position, center the map around
		self.playerRoom = currentRoom
		self.draw_map(currentRoom.x, currentRoom.y, currentRoom.z)

	def on_guiRefresh(self) -> None:
		"""This event is fired when the mapper needs to signal the GUI to clear
		the visible rooms cache and redraw the map view."""
		self.draw_map(self.cx, self.cy, self.cz)
		logger.debug("GUI refreshed.")

	def draw_map(self, cx, cy, cz) -> None:
		logger.debug(f"Drawing rooms around ({cx}, {cy}, {cz}).")
		# reset the recorded state of the window
		self.sprites.clear()
		self.visibleRooms.clear()
		self.cx = cx
		self.cy = cy
		self.cz = cz
		# draw the rooms, beginning by the central one
		for vnum, room, x, y, z in self.world.getNeighbors(cx, cy, cz, radius=self.radius):
			if z == 0:
				self.draw_room(self.mcol + x, self.mrow + y, room)
		self.draw_player()

	def draw_room(self, x: int, y: int, room):
		logger.debug(f"Drawing room: {x} {y} {room.vnum}")
		self.visibleRooms[x, y] = room
		# draw the terrain on layer 0
		if room.light == "dark":
			self.draw_tile(x, y, 0, room.terrain + "-dark")
		else:
			self.draw_tile(x, y, 0, room.terrain)
		# draw the walls on layer 1
		direction: str
		for direction in ("north", "east", "south", "west"):
			if direction not in room.exits:
				self.draw_tile(x, y, 1, "wall" + direction)
		# draw the arrows for exits up and down on layer 1
		for direction in ("up", "down"):
			if direction in room.exits:
				self.draw_tile(x, y, 1, "exit" + direction)
		# draw a single flag on layer 2
		flagged = False
		for flag in DISPLAY_FLAGS:
			if flag in room.flags:
				self.draw_tile(x, y, 2, DISPLAY_FLAGS[flag])
				flagged = True
		if not flagged and room.label:
			self.draw_tile(x, y, 2, "label")
		# show highlighted rooms (path and find results)
		if room.highlight:
			self.draw_tile(x, y, 2, "path")
		# Highlights rooms without serverid
		if room.serverid == "0":
			self.draw_tile(x, y, 2, "noid")

	def draw_player(self) -> None:
		if self.playerRoom is None:
			return None
		logger.debug(f"Drawing player on room vnum {self.playerRoom.vnum}")
		# transform map coordinates to window ones
		x: int = self.playerRoom.x - self.cx + self.mcol
		y: int = self.playerRoom.y - self.cy + self.mrow
		z: int = self.playerRoom.z - self.cz
		# Be sure the player coordinates are part of the window
		if z == 0 and x >= 0 and x < self.col and y >= 0 and y < self.row:
			# draw the player on layer 3
			self.draw_tile(x, y, 3, self.world.playerTile)

	def draw_tile(self, x: int, y: int, z: int, tile: str) -> None:
		logger.debug(f"Drawing tile: {x} {y} {tile}")
		# pyglet stuff to add a sprite to the batch
		sprite: SpriteType
		sprite = pyglet.sprite.Sprite(TILES[tile], batch=self.batch, group=self.layer[z])
		# adapt sprite coordinates
		sprite.x = x * self.square
		sprite.y = y * self.square
		# add the sprite to the list of visible sprites
		self.sprites.append(sprite)

	def on_mouse_press(self, wx: int, wy: int, buttons: int, modifiers: int) -> None:
		logger.debug(f"Mouse press on {wx} {wy}.")
		x: int = int(wx / self.square)
		y: int = int(wy / self.square)
		cx, cy = self.getWorldCoordinates(x, y)
		# Action depends on which button the player clicked
		if buttons == pyglet.window.mouse.LEFT:
			logger.debug(f"Left click on {wx} {wy}.")
			# center the map on the selected room
			self.draw_map(cx, cy, self.cz)
		elif buttons == pyglet.window.mouse.MIDDLE:
			logger.debug(f"Middle click on {wx} {wy}.")
			# center the map on the player
			if self.playerRoom is not None:
				self.draw_map(self.playerRoom)
			else:
				logger.warning("Unable to center the map on the player. The player room is not defined.")
		elif buttons == pyglet.window.mouse.RIGHT:
			logger.debug(f"Right click on {wx} {wy}.")
			# check if the player clicked on a room
			if (x, y) in self.visibleRooms:
				self.selectedRoom = self.visibleRooms[x, y]
				self.world.echo(f"Click on room {self.selectedRoom.vnum} ({self.selectedRoom.x}, {self.selectedRoom.y}, {self.selectedRoom.z}).")
			else:
				self.world.echo(f"Click on coordinates ({cx}, {cy}, {self.cz}).")

	#def on_mouse_release(self, wx, wy, buttons, modifiers):
	#	if buttons != pyglet.window.mouse.RIGHT:
	#		return
	#	logger.debug(f"Mouse release on {wx} {wy}.")
	#	x: int = int(wx / self.square)
	#	y: int = int(wy / self.square)
	#	cx, cy = self.getWorldCoordinates(x, y)
	#	if self.selectedRoom.x != cx or self.selectedRoom.y != cy:
	#		print(f"moving {self.selectedRoom.vnum} ({self.selectedRoom.x}, {self.selectedRoom.y}, {self.selectedRoom.z}) to ({cx}, {cy}, {self.selectedRoom.z}).")

	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		if buttons != pyglet.window.mouse.RIGHT:
			return
		for sprite in self.sprites:
			if sprite.x < x < sprite.x + sprite.width and sprite.y < y < sprite.y + sprite.width:
				sprite.x += dx
				sprite.y += dy

	def on_key_press(self, symbol, modifiers):
		x = self.cx
		y = self.cy
		if symbol == pyglet.window.key.H:
			x -= 1
		elif symbol == pyglet.window.key.J:
			y -= 1
		elif symbol == pyglet.window.key.K:
			y += 1
		elif symbol == pyglet.window.key.L:
			x += 1
		# center the map on the selected room
		self.draw_map(x, y, self.cz)


Window.register_event_type("on_mapSync")
Window.register_event_type("on_guiRefresh")

class GuiThread(threading.Thread):
	def __init__(self, world):
		threading.Thread.__init__(self)
		# daemon threads terminates when main process does
		self.daemon = True
		self.world = world

	def run(self):
		w = Window(self.world)
		pyglet.app.run()
