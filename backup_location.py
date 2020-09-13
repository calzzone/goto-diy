
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
last_location_file = "/home/pi/last_location_file.txt" # keep a record of the last known location (coordinates, body, time)
def recover_last_location():
	global last_location_file
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


def save_location():
	global last_location_file
	with open(last_location_file, "w") as f:
		line = str(azimuth) + ";" + str(altitude) + ";" + same + ";" + str(datetime.utcnow()) + "\n"
		f.write(line)


################## set curent location

def set_location():
	global azimuth
	global altitude

	#azimuth, altitude = map(float, input("Current Az Alt: ").split())
	new_azimuth, new_altitude = search()
	if (new_azimuth == None or new_altitude == None):
		return()

	azimuth  = new_azimuth % 360.0
	altitude = new_altitude  % 360.0

	save_location()
