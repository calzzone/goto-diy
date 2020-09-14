
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

# global variables
import config
from config import *

import backup_location # for save_location() in set_location()

################## setup functions

def set_speed():
	#global delay_ALT
	#global speed_ALT
	#global delay_AZ
	#global speed_AZ

	config.speed_AZ, config.speed_ALT = map(float, input("Speed for Az Alt (deg/second): ").split())

	config.delay_AZ = 360.0 / (config.speed_AZ * config.steps_per_rotation_AZ * 2.0)
	print ("Time to complete 0 to 360 deg rotation (Az): " +  str(360.0 / config.speed_AZ) + " seconds.")
	print ("delay (Az): " + str(config.delay_AZ) + " seconds.")

	config.delay_ALT = 360.0 / (config.speed_ALT * config.steps_per_rotation_ALT * 2.0)
	print ("Time to complete 0 to 90 deg rotation (Alt): " +  str(90.0 / config.speed_ALT) + " seconds.")
	print ("delay (Alt): " + str(config.delay_ALT) + " seconds.")

# TODO: when micros changes, does location stay the same?
def set_microstepping():
	#global microstep_az
	#global microstep_alt
	#global steps_per_rotation_AZ
	#global steps_per_rotation_ALT

	print("Enable / disable microstepping in Az and Alt axes")
	config.microstep_az, config.microstep_alt = input("Az Alt microstepping resolution ( Full, 1/2-1/32 ): ").split()

	GPIO.output(MODE_AZ, MICROSTEP_RESOLUTION[config.microstep_az])
	config.steps_per_rotation_AZ = SPR_BASE_AZ * MICROSTEP_FACTOR[ config.microstep_az ]

	GPIO.output(MODE_ALT, MICROSTEP_RESOLUTION[config.microstep_alt])
	config.steps_per_rotation_ALT = SPR_BASE_ALT * MICROSTEP_FACTOR[ config.microstep_alt ]

	print ("Step size (Az): " + str( 360.0 / config.steps_per_rotation_AZ ) + " degrees. Microstepping: " + config.microstep_az + " .")
	print ("Step size (Alt): " + str( 360.0 / config.steps_per_rotation_ALT ) + " degrees. Microstepping: " + config.microstep_alt + " .")


# when in tracking mode, update every ... seconds
def set_track_refresh_interval():
	#global track_refresh_interval
	config.track_refresh_interval = float(input("Tracking refresh interval (seconds): "))

################## set curent location

def set_location():
	#global azimuth
	#global altitude

	#azimuth, altitude = map(float, input("Current Az Alt: ").split())
	new_azimuth, new_altitude = search()
	if (new_azimuth == None or new_altitude == None):
		return()

	config.azimuth  = new_azimuth % 360.0
	config.altitude = new_altitude  % 360.0

	backup_location.save_location()
