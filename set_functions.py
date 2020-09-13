
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


################## setup functions

def set_speed():
	global delay_ALT
	global SPEED_ALT
	global delay_AZ
	global SPEED_AZ

	SPEED_AZ, SPEED_ALT = map(float, input("Speed for Az Alt (deg/second): ").split())

	delay_AZ = 360.0 / (SPEED_AZ * SPR_AZ * 2.0)
	print ("Time to complete 0 to 360 deg rotation (Az): " +  str(360.0 / SPEED_AZ) + " seconds.")
	print ("delay (Az): " + str(delay_AZ) + " seconds.")

	delay_ALT = 360.0 / (SPEED_ALT * SPR_ALT * 2.0)
	print ("Time to complete 0 to 90 deg rotation (Alt): " +  str(90.0 / SPEED_ALT) + " seconds.")
	print ("delay (Alt): " + str(delay_ALT) + " seconds.")

# TODO: when micros changes, does location stay the same?
def set_microstepping():
	global microstep_az
	global microstep_alt
	global SPR_AZ
	global SPR_ALT

	print("Enable / disable microstepping in Az and Alt axes")
	microstep_az, microstep_alt = input("Az Alt microstepping resolution ( Full, 1/2-1/32 ): ").split()

	GPIO.output(MODE_AZ, MICROSTEP_RESOLUTION[microstep_az])
	SPR_AZ = SPR_BASE_AZ * MICROSTEP_FACTOR[ microstep_az ]

	GPIO.output(MODE_ALT, MICROSTEP_RESOLUTION[microstep_alt])
	SPR_ALT = SPR_BASE_ALT * MICROSTEP_FACTOR[ microstep_alt ]

	print ("Step size (Az): " + str( 360.0 / SPR_AZ ) + " degrees. Microstepping: " + microstep_az + " .")
	print ("Step size (Alt): " + str( 360.0 / SPR_ALT ) + " degrees. Microstepping: " + microstep_alt + " .")


# when in tracking mode, update every ... seconds
def set_track_refresh_interval():
	global track_refresh_interval
	track_refresh_interval = float(input("Tracking refresh interval (seconds): "))

################## backup location

# whenever the current location changes, update a file just in case.
# one could reterive back the information and restart at the last kown location

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
