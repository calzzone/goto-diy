
from time import sleep
from getkey import getkey, keys
from datetime import datetime

import os
#print (os.path.abspath(os.getcwd()))

import signal
import sys
from threading import Timer
from readchar import readkey

import string
import math

import ephem
from ephem import *

################## backup location

# whenever the current location changes, update a file just in case.
# one could reterive back the information and restart at the last kown location

def save_location():
	with open(last_location_file, "w") as f:
		line = str(azimuth) + ";" + str(altitude) + ";" + same + ";" + str(datetime.utcnow()) + "\n"
		f.write(line)

def recover_last_location():
	with open(last_location_file) as f:
		# Look at each line of the file
		for line in f:
			line=line.strip()

			# Skip comments
			if line.startswith('#'):
				continue

			pound = line.find("#")
			if pound >= 0:
				line = line[:pound]

			# Split the line apart.
			elements = line.split(";")
			break # 1 record only

	global azimuth
	global altitude
	global same
	if len(elements) >= 2:
		azimuth = float(elements[0])
		altitude = float(elements[1])
		print ("Recovered last location: Az " + str(azimuth) + " Alt " + str(altitude) + ".")
	if len(elements) >= 3:
		if elements[2] != "":
			same = elements[2]
			print ("Recovered last successfull searched location: " + same + ".")
