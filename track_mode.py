
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

from print_functions import * # soon to be implemented...
from ephem_wrapper import *
from load_landmarks import *
from backup_location import *
from move_function import *
from move_1_step import *
from move_1_deg import *

################## track

# Countdown in tracking mode.
def countdown(*args):
	print("Next move in " + str(args[0]) + " seconds...")
	if args[0] <= 1: os.kill(args[1], signal.SIGINT)

# in tracking moe,teh user searches for a body, the program goes there and then recomputes its coordonates and moves accordingly every few seconds
# meanwhile, the user can manually fine-tune the position of the telescope so the actual position coresponds to the position the software thinks it should be pointing to

# accept keyboard input (c or tuning directions) while waiting between moves
# the regular getkey method is not good because it does not expire after a set timeout
def wait_for(timeout):
	pid = os.getpid()
	sig = signal.SIGINT
	timer = Timer(timeout, lambda: os.kill(pid, sig))
	timer.start()  # spawn a worker thread to interrupt us later
	print(f"Auto-tracking with manual control. Press 'c' to cancel, ? / ! to get status. Next move in {timeout} seconds. ")

	# spawn many delayed prints, one for every second in timeout
	#timers = [Timer(i, countdown, (timeout-i, pid)) for i in range(int(round(timeout, 0)))]
	timers = [Timer(i, lambda: print("Next move in " + str(timeout-i) + " seconds...")) for i in range(int(round(timeout, 0)))]
	for t in timers: t.start()


	#paused = False
	while True:
		key = readkey()
		#print(f"received {k!r}")
		if key == 'c':
			print("Exiting tracking mode...")
			timer.cancel()  # cancel the timer
			return (True)
		#elif key == 'p' and not paused:
			#print("Pausing tracking mode...")
			#paused = True
			#timer.cancel()  # pause the timer
		#elif key == 'p' and paused:
			#print("Resuming tracking mode...")
			#paused = False
			##timer.start()  # resume the timer
			#return(False)
		elif key == '?': print_location()
		elif key == '!': print_status()
		elif key == keys.UP: up_1_step(update_position = False)
		elif key == keys.DOWN: down_1_step(update_position = False)
		elif key == keys.LEFT: left_1_step(update_position = False) #
		elif key == keys.RIGHT: right_1_step(update_position = False) #
		elif key == 'w': up_1(update_position = False)
		elif key == 's': down_1(update_position = False)
		elif key == 'a': left_1(update_position = False) #
		elif key == 'd': right_1(update_position = False)

	#return (None)

def track():
	# step 1: search for something to track (TODO track coordinates)
	found = False
	while not found:
		same_str_builder = ": " + config.same_str if config.same_str != "" else ""
		print("Search for celestial body. To list stars in YBS catalogue type 'named' or 'all'. To list landmakrs type 'landmarks'.")
		location = input("Location (common name, 'same`" + same_str_builder + " or 'c' to cancel): ")

		if location == "named":
			print_named_stars()
			continue
		if location == "all":
			print_available_stars()
			continue
		if location == "landmakrs":
			print_landmarks()
			continue

		if location == 'c': return ()

		if location == "same":
			location = config.same

		location_coord = search_0(location)

		if location_coord is None:
			print("Not found. Try again. ")
			continue

		if location_coord[0] < 0 or location_coord[0] >= 360 or location_coord[1] < 0 or location_coord[1] > 90:
			print("Outside valid and / or trackable ranges. Try again. ")
			continue

		found = True

	target_az, target_alt = location_coord[0], location_coord[1]


	# step 2: track: move, wait for ... seconds while accepting keybord input, search again
	while not (target_az < 0 or target_az >= 360 or target_alt < 0 or target_alt > 90):
		#print("c to cancel, ? to get status.")
		#key = getkey()
		#if key == '?': print_location()
		#elif key == 'c': break

		print ("Will move Az from " + str(config.azimuth) + " to " + str(target_az) + " and Alt from " + str(config.altitude) + " to " + str(target_alt))


		Az = config.azimuth + 360.0
		TAz = target_az + 360.0
		delta_az_right = (TAz - Az) % 360.0
		delta_az_left  = (Az - TAz) % 360.0

		delta_az = min(delta_az_right, delta_az_left)
		direction_az = ("left", "right")[delta_az_right < delta_az_left]

		if config.altitude > 180: delta_alt = target_alt - config.altitude + 360
		else: delta_alt = target_alt - config.altitude
		direction_alt = ("down", "up")[delta_alt > 0.0]

		move(amount_az = delta_az, direction_az = direction_az, speed_az = config.speed_AZ,
			amount_alt = abs(delta_alt), direction_alt = direction_alt, speed_alt = config.speed_ALT)

		# accept keyboard input (c or tuning directions) while waiting between moves
		#sleep(track_refresh_interval)
		try:
			if wait_for( config.track_refresh_interval ) ==  True: break
		except KeyboardInterrupt as err: # accept Ctrl+c
			pass

		#print ("...next move now...")
		target_az, target_alt = search_0(location)
