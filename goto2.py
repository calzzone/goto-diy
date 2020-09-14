### This is the main code file f my telescope control software.


# https://git.nexlab.net/astronomy/skylived/tree/bd59190026d9d95b39983f8a0106a7e17023aee8/DecraDB/xephemdb
# https://github.com/Alex-Broughton/StarAtlas

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

# Raspberry Pi GPIO access
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# global variables
import config
from config import *

from load_observers import *
config.observers = gather_observers(config.observers_file)
config.observer, config.observer_name = set_observer(config.observer_name)

from load_landmarks import *
config.landmarks = gather_landmarks(config.landmarks_file)

from backup_location import * # CRITICAL: before set_functions
from ephem_wrapper import *

from set_functions import * # CRITICAL: after backup_location
from move_function import *
from move_1_step import *
from move_1_deg import *
from manual_drive_mode import *
from scan_sky_mode import *
from go_to_mode import *
from track_mode import *





################## main

def quit_nicely():
	GPIO.cleanup()
	print ("good riddance!")


def show_options():
	print ("\nAvailable options:")
	print ("0: Quit nicely")
	print ("1-4: Operating modes: track (1), move (2), manual drive (3) , scan sky area (4)")
	print ("5-9: Set: speed (5), microstepping (6), track refresh interval (7), observer (8), current coordinates (9)")
	print ("10: Recover last recoded coordinates")
	print ("18 19 20: Print: observer (18), current coordinates (19), status (20)")
	print ("21-23: Print: named stars (21), all available stars in YBS (22), landmakrs (23)")
	print ("31: Make fake star")

def switch_main(option):
	switcher = {
		0: quit_nicely,

		1: track,
		2: go_to_location,
		3: manual_drive,
		4: scan_sky,

		5: set_speed,
		6: set_microstepping,
		7: set_track_refresh_interval,
		8: set_observer,
		9: set_location,
		10: recover_last_location,

		18: print_observer,
		19: print_location,
		20: print_status,

		21: print_named_stars,
		22: print_available_stars,
		23: print_landmarks,

		31: make_fake_star
	}
	func = switcher.get(option, show_options)
	func()

################

def main():
	recover_last_location()
	show_options()
	option = int(input("what is my purpose? "))
	while option != 0:
		switch_main(option)
		show_options()
		option = int(input("what is my purpose? "))

	#GPIO.cleanup()
	quit_nicely()

if __name__ == '__main__':
	main()




#GPIO.cleanup()
quit_nicely()
