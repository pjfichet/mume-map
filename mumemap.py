#! /usr/bin/env python

import sys
import os

def usage():
	print("Usage:")
	print("mumemap -e map.json                      # start emulation")
	print("mumemap -u map.json new.json out.json    # update map file")
	print("mumemap -f map.json out.json             # fix map flags")

def fileexists(file):
	if not os.path.exists(file):
		print(f"Error: {file} does not exist. Aborting.")
		exit()
	elif os.path.isdir(file):
		print(f"Error: {file} is a directory, not a file. Aborting.")
		exit()

def fileexistsnot(file):
	if os.path.exists(file):
		print(f"Error: {file} exists. Aborting.")
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
	fileexists(sys.argv[2])
	fileexists(sys.argv[3])
	fileexistsnot(sys.argv[4])
	from mumemap.update import Update
	u = Update()
	u.update(sys.argv[2], sys.argv[3], sys.argv[4])
elif len(sys.argv) == 4 and sys.argv[1] == "-f":
	# fix flags
	fileexists(sys.argv[2])
	fileexistsnot(sys.argv[3])
	from mumemap.fixflags import FixFlags
	f = FixFlags()
	f.fix(sys.argv[2], sys.argv[3])
else:
	usage()
		
