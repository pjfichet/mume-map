import re

ROOTS_REGEX = re.compile(
	r"Some roots lie here waiting to ensnare weary travellers\.|"
	r"The remains of a clump of roots lie here in a heap of rotting compost\.|"
	r"A clump of roots is here, fighting|"
	r"Some withered twisted roots writhe towards you\.|"
	r"Black roots shift uneasily all around you\.|"
	r"black tangle of roots|"
	r"Massive roots shift uneasily all around you\.|"
	r"rattlesnake"
)

def fixRoom(room):
	# flag all rattlesnakes
	if 'rattlesnake' in room.dynadesc:
		if 'rattlesnake' not in room.mobFlags:
			room.mobFlags.append('rattlesnake')
	# roots deserve a flag
	if ROOTS_REGEX.search(room.dynadesc):
		room.mobFlags.append('roots')
	# these mobs are aggressive mobs
	# these mobs are elite mobs
	# these mobs are super mobs
	return room



TERRAIN_COSTS: dict[str, float] = {
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
VALID_MOB_FLAGS: tuple[str, ...] = (
	# in gui: guild, quest, rent, shop, aggressive
	"rent",
	"shop",
	"weapon_shop",
	"armour_shop",
	"food_shop",
	"pet_shop",
	"guild",
	"scout_guild",
	"mage_guild",
	"cleric_guild",
	"warrior_guild",
	"ranger_guild",
	"aggressive_mob", # almost everything...
	"quest_mob",
	"passive_mob",
	"elite_mob", # a dozen mobs
	"super_mob", # 4 rooms
	"milkable",
	"rattlesnake",
)
VALID_LOAD_FLAGS: tuple[str, ...] = (
	# in gui: attention, armour, herb, key, treasure, weapon
	"treasure",
	"armour",
	"weapon",
	"water",
	"food",
	"herb",
	"key",
	"mule",
	"horse",
	"pack_horse",
	"trained_horse",
	"rohirrim",
	"warg",
	"boat",
	"attention",
	"tower",  # Player can 'watch' surrounding rooms from this one.
	"clock",
	"mail",
	"stable",
	"white_word",
	"dark_word",
	"equipment",
	"coach",
	"ferry",
)
VALID_EXIT_FLAGS: tuple[str, ...] = (
	"avoid",
	"exit",
	"door",
	"road",
	"climb",
	"random",
	"special",
	"no_match",
	"flow",
	"no_flee",
	"damage",
	"fall",
	"guarded",
)
VALID_DOOR_FLAGS: tuple[str, ...] = (
	"hidden",
	"need_key",
	"no_block",
	"no_break",
	"no_pick",
	"delayed",
	"callable",
	"knockable",
	"magic",
	"action",  # Action controlled
	"no_bash",
)
