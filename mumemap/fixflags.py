import os
import json
import re
from . import flags


class FixFlags:
	def __init__(self):
		self.oldjson = {}
		self.newjson = {}
		self.notes = 0
		self.rattlesnakes = 0
		self.roots = 0
		self.flags = {}
		for flag in flags.MOB_FLAGS:
			self.flags[flag] = 0
		for flag in flags.LOAD_FLAGS:
			self.flags[flag] = 0


	def load(self, file):
		if not os.path.exists(file):
			print(f"Error: {file} does not exist.")
			exit(1)
		elif os.path.isdir(file):
			print(f"Error {file} is a directory, not a file.")
			exit(1)
		with open(file, "rb") as f:
			return json.load(f)

	def fix(self, oldfile, newfile):
		self.oldjson = self.load(oldfile)
		for vnum, room in self.oldjson.items():
			if vnum != "schema_version":
				self.fix_ingredients(vnum, room)
				self.fix_rattlesnakes(vnum, room)
				self.fix_roots(vnum, room)
				#self.fix_attention(vnum, room)
				#self.countflags(room)
		data = json.dumps(self.oldjson, sort_keys=True, indent=2)
		with open(newfile, "w") as f:
			f.write(data)
		print(f"Fixed {self.notes} notes, {self.rattlesnakes} rattlesnakes and {self.roots} roots.")
		#print(self.flags)

	def fix_ingredients(self, vnum, room):
		if 'ingredients' not in room:
			room['ingredients'] = []
		note = room['note'].lower()
		note = re.sub(',\n', ', ', note)
		note = re.sub('\n', ', ', note)
		for key in flags.NOTES_SUBSTITUTIONS:
			note = re.sub(key, flags.NOTES_SUBSTITUTIONS[key], note)
		note = note.strip(' ').strip(',').strip('.')
		toadd = False
		notelist = note.split(',')
		newlist = notelist.copy()
		for item in notelist:
			i = item.strip(' ')
			if i in flags.INGREDIENTS_FLAGS:
				room['ingredients'].append(i)
				toadd = True
				newlist.remove(item)
			elif i:
				for j in i.split(' '):
					if j in flags.INGREDIENTS_FLAGS:
						room['ingredients'].append(j)
						toadd = True
						toprint = True
		# rewrite the note
		room['note'] = ",".join(newlist).strip(' ')
		#if room['ingredients'] and room['note']:
		#	print(f"{vnum}:\n\t{room['note']}\n\t{room['ingredients']}")
		if toadd:
			self.notes += 1

	def fix_rattlesnakes(self, vnum, room):
		# add rattlesnake to mob_flags
		if 'rattlesnake' not in room['mob_flags']:
			if 'rattlesnake' in room['note']:
				room['mob_flags'].append('rattlesnake')
				room['note'] = re.sub(r'rattlesnake( |, |)', '', room['note'])
				self.rattlesnakes += 1
			elif 'rattlesnake' in room['contents']:
				room['mob_flags'].append('rattlesnake')
				self.rattlesnakes += 1
			elif 'rattlesnake' in room['ingredients']:
				room['mob_flags'].append('rattlesnake')
				self.rattlesnakes += 1
		if 'rattlesnake' in room['mob_flags'] and 'attention' in room['load_flags']:
				room['load_flags'].remove('attention')

	def fix_roots(self, vnum, room):
		if 'roots' not in room['mob_flags']:
			if 'roots' in room['note']:
				room['mob_flags'].append('roots')
				room['note'] = re.sub(r'roots( |, |)', '', room['note'])
				self.roots += 1
			elif flags.ROOTS_REGEX.search(room['contents']):
				room['mob_flags'].append('roots')
				self.roots += 1
		if 'roots' in room['mob_flags'] and 'attention' in room['load_flags']:
				room['load_flags'].remove('attention')

	def fix_attention(self, vnum, room):
		if 'attention' in room['load_flags']:
			flags = ", ".join(room['mob_flags'] + room['load_flags'])
			print(f"{vnum} {room['name']}:\n{room['note']} - {flags}")

	def countflags(self, room):
		for flag in room['mob_flags']:
			if flag in self.flags:
				self.flags[flag] += 1
		for flag in room['load_flags']:
			if flag in self.flags:
				self.flags[flag] += 1