import os
import json
from difflib import SequenceMatcher
from fmt import *

class Update:
	def __init__(self):
		self.oldjson = {}
		self.newjson = {}
		self.newrooms = 0
		self.newserverids = 0

	def update(self, oldfile, newfile, outfile):
		self.oldjson = self.load(oldfile)
		self.newjson = self.load(newfile)
		if "schema_version" in self.newjson:
			del self.newjson['schema_version']
		for vnum, room in self.newjson.items():
			self.updateroom(vnum, room)
		for vnum, room in self.oldjson.items():
			if vnum not in self.newjson:
				self.newjson[vnum] = room
		data = json.dumps(self.oldjson, sort_keys=True, indent=2)
		with open(outfile, "w") as f:
			f.write(data)
		print(f"Added {self.newrooms} rooms and {self.newserverids} server_ids.")

	def load(self, file):
		if not os.path.exists(file):
			print(f"Error: {file} does not exist.")
			exit(1)
		elif os.path.isdir(file):
			print(f"Error {file} is a directory, not a file.")
			exit(1)
		with open(file, "rb") as f:
			return json.load(f)

	def updateroom(self, vnum, newroom):
		if vnum not in self.oldjson:
			print(f"{vnum}: new room.")
			newroom['label'] = ''
			self.newrooms += 1
			return
		### check oldroom
		oldroom = self.oldjson[vnum]
		# server_id
		if newroom['server_id'] == '0' and oldroom['server_id'] != '0':
			newroom['server_id'] = oldroom['server_id']
			self.newserverids += 1
			#print(f"{vnum}: add server_id {newroom['server_id']}")
		elif newroom['server_id'] != newroom['server_id']:
			print(f"{vnum}: server_id differ.")
		# label
		if oldroom['label']:
			newroom['label'] = oldroom['label']
		if oldroom['name'] != newroom['name'] or oldroom['description'] != newroom['description']:
			oldname = stringAscii(oldroom['name']).lower()
			newname = stringAscii(newroom['name']).lower()
			olddesc = stringAscii(oldroom['description']).lower()
			newdesc = stringAscii(newroom['description']).lower()
			if oldname != newname or olddesc != newdesc:
				nameratio = SequenceMatcher(None, oldname, newname).ratio()
				descratio = SequenceMatcher(None, olddesc, newdesc).ratio()
				if nameratio < 0.9 or descratio < 0.8:
					print(f"{vnum}: description differ ({nameratio}, {descratio}).")		

