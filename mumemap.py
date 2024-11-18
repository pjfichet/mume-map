#! /usr/bin/env python

import sys
import os

def usage():
	print("Usage:")
	print("mumemap -e map.json                      # start emulation")
	print("mumemap -u map.json new.json out.json    # update map file")

def fileexists(file):
	if not os.path.exists(file):
		print(f"Error: {file} does not exist.")
		exit()
	elif os.path.isdir(file):
		print(f"Error: {file} is a directory, not a file.")
		exit()

if len(sys.argv) == 2 and sys.argv[1] == "-h":
	# help
	usage()
elif len(sys.argv) == 3 and sys.argv[1] == "-e":
	# emulation
	fileexists(sys.argv[2])
	from mumemap.emu import Emulation
	e = Emulation()
	e.log('map.log', 4, False)
	e.run(sys.argv[2])
elif len(sys.argv) == 5 and sys.argv[1] == "-u":
	# update
	filexists(sys.argv[2])
	filexists(sys.argv[3])
	if os.path.exists(sys.argv[4]):
		print(f"Error: {sys.argv[4]} exists.")
		exit()
	from .update import Update
	u = Update()
	u.update(sys.argv[2], sys.argv[3], sys.argv[4])
else:
	usage()
		
