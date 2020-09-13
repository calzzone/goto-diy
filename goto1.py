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

from load_settings import *



################## other parameters

same = "0 0" # keep track of the last successfull searched location. TODO: fix the bug whih affects last_location_file
same_str = "" # print-ready version of same (only when same is a body)

last_location_file = "/home/pi/last_location_file.txt" # keep a record of the last known location (coordinates, body, time)
print(last_location_file)
# When in tracking mode, update every x seconds
track_refresh_interval = 20


from load_observers import *
from load_landmarks import *
from backup_location import *
from ephem_wrapper import *

from set_functions import *
from move_to_mode import *
from move_1_step import *
from move_1_deg import *
from manual_drive_mode import *
from scan_sky_mode import *



# let the user specify a location (coordinates or named body) and go there
def go_to_location():
	target_az =  -1
	target_alt = -1
	while target_az < 0 or target_az >= 360 or target_alt < 0 or target_alt > 90:
		#target_az, target_alt = map(float, input("Target Az [0-360) Alt [0-90 deg]: (-360 to cancel) ").split())
		target_az, target_alt = search()
		if (target_alt == None or target_az == None):
			return()
		if (target_alt == altitude and target_az == azimuth):
			return()

	if azimuth != target_az:
		print ("Will move Az from " + str(azimuth) + " to " + str(target_az))
	if altitude != target_alt:
		print ("Will move Alt from " + str(altitude) + " to " + str(target_alt))

#	delta_az = abs(target_az - azimuth)
#	delta_az %= 360.0
#	delta_az = 180.0 - abs(delta_az - 180.0)
#	if (azimuth + delta_az) % 360.0 == target_az:
#		direction_az = "right"
#	else: direction_az = "left"

	Az = azimuth + 360.0
	TAz = target_az + 360.0
	delta_az_right = (TAz - Az) % 360.0
	delta_az_left  = (Az - TAz) % 360.0

	delta_az = min(delta_az_right, delta_az_left)
	direction_az = ("left", "right")[delta_az_right < delta_az_left]

	if altitude > 180: delta_alt = target_alt - altitude + 360 # TODO: should not happen under regular usage!
	else: delta_alt = target_alt - altitude
	direction_alt = ("down", "up")[delta_alt > 0.0]

	move(amount_az = delta_az, direction_az = direction_az, speed_az = SPEED_AZ,
		amount_alt = abs(delta_alt), direction_alt = direction_alt, speed_alt = SPEED_ALT)


################## track

# in tracking moe,teh user searches for a body, the program goes there and then recomputes its coordonates and moves accordingly every few seconds
# meanwhile, the user can manually fine-tune the position of the telescope so the actual position coresponds to the position the software thinks it should be pointing to

# accept keyboard input (c or tuning directions) while waiting between moves
# the regular getkey method is not good because it does not expire after a set timeout
def wait_for(timeout):
	pid = os.getpid()
	sig = signal.SIGINT
	timer = Timer(timeout, lambda: os.kill(pid, sig))
	print(f"Auto-tracking with maual control. Press 'c' to cancel, ? / ! to get stauts. Next move in {timeout} seconds. ")
	timer.start()  # spawn a worker thread to interrupt us later
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
		same_str_builder = ": " + same_str if same_str != "" else ""
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
			location = same

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

		print ("Will move Az from " + str(azimuth) + " to " + str(target_az) + " and Alt from " + str(altitude) + " to " + str(target_alt))

		######### changhed ti the same algoritm as in go_to_location()

		#delta_az = abs(target_az - azimuth)
		#delta_az %= 360.0
		#delta_az = 180.0 - abs(delta_az - 180.0)
		#if (azimuth + delta_az) % 360.0 == target_az:
			#direction_az = "right"
		#else: direction_az = "left"

		Az = azimuth + 360.0
		TAz = target_az + 360.0
		delta_az_right = (TAz - Az) % 360.0
		delta_az_left  = (Az - TAz) % 360.0

		delta_az = min(delta_az_right, delta_az_left)
		direction_az = ("left", "right")[delta_az_right < delta_az_left]

		if altitude > 180: delta_alt = target_alt - altitude + 360
		else: delta_alt = target_alt - altitude
		direction_alt = ("down", "up")[delta_alt > 0.0]

		move(amount_az = delta_az, direction_az = direction_az, speed_az = SPEED_AZ,
			amount_alt = abs(delta_alt), direction_alt = direction_alt, speed_alt = SPEED_ALT)

		# accept keyboard input (c or tuning directions) while waiting between moves
		#sleep(track_refresh_interval)
		try:
			if wait_for( track_refresh_interval ) ==  True: break
		except KeyboardInterrupt as err: # accept Ctrl+c
			pass

		#print ("...next move now...")
		target_az, target_alt = search_0(location)





################## print info


def print_location():
	print("Curent Az: " + str(azimuth) + ", Alt: " + str(altitude))

def print_status():
	print_location()
	if same != "": print ("Last successfull searched body:" + same)

	print("Speed Az: " + str(SPEED_AZ) + ", Alt: " + str(SPEED_ALT))
	print ("Time to complete 0 to 360 deg rotation (Az): " +  str(360.0 / SPEED_AZ) + " seconds.")
	print ("delay (Az): " + str(delay_AZ) + " seconds.")

	print ("Time to complete 0 to 90 deg rotation (Alt): " +  str(90.0 / SPEED_ALT) + " seconds.")
	print ("delay (Alt): " + str(delay_ALT) + " seconds.")

	print("Microstepping Az: " + str(microstep_az) + ", Alt: " + str(microstep_alt))

	print("Track refresh interval: " + str(track_refresh_interval) + " seconds." )









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

print("before main")
print(last_location_file)

def main():
	print("main")
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
