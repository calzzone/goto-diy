
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
from backup_location import *
from move_function import *
from move_1_step import *
from move_1_deg import *

######### Scan sky

# accept keyboard input (c or tuning directions) while waiting between moves
# the regular getkey method is not good because it does not expire after a set timeout
def wait_for_scan_sky(timeout):
	pid = os.getpid()
	sig = signal.SIGINT
	timer = Timer(timeout, lambda: os.kill(pid, sig))
	print(f"Press 'c' to cancel, ? / ! to get stauts. Next move in {timeout} seconds. ")
	timer.start()  # spawn a worker thread to interrupt us later
	#paused = False
	while True:
		key = readkey()
		#print(f"received {k!r}")
		if key == 'c':
			print("Exiting scanning mode...")
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

	#return (None)

# moves around the current location to allow the user to spot a body
def scan_sky():

	# defaults for WA15 eypeice
	#amount_total = 5
	#amount_step = 0.5
	#pause = 2

	amount_total, amount_step, pause =  map(float, input("Total area scaned (degrees), increment size (degrees) and cooldwon pause between steps (seconds): ").split())

	# start in the lower left corner of the scan area
	# I am now in the center of the area
	# move half the scaing area, down and left, from the center of the area
	steps = int(math.ceil(amount_total/amount_step))
	print("Steps / row: " + str(steps))
	move(amount_az = -amount_step*steps/2, direction_az = "right", speed_az = config.speed_AZ,
		 amount_alt = -amount_step*steps/2, direction_alt = "up", speed_alt = config.speed_ALT,
		 update_position = False)

	#sleep (pause) # wait to spot something
	try:
		if wait_for_scan_sky( pause ) ==  True: return()
	except KeyboardInterrupt as err: # accept Ctrl+c
		pass

	# move 1 step at a time, upwords, right then left, row by row
	#steps = int(math.ceil(amount_total/amount_step))
	for i in range(steps): # azimuth
		for j in range(steps): # altitude

			# change direction between rows
			if i % 2 == 0: direction_az = "right"
			else: direction_az = "left"


			move(amount_az = amount_step, direction_az = direction_az, speed_az = config.speed_AZ,
				amount_alt = 0, direction_alt = "up", speed_alt = config.speed_ALT,
				update_position = False)

			#sleep (pause) # wait to spot something
			try:
				if wait_for_scan_sky( pause ) ==  True: return()
			except KeyboardInterrupt as err: # accept Ctrl+c
				pass

		# next row
		move(amount_az = 0, direction_az = "right", speed_az = 1.0,
			amount_alt = amount_step, direction_alt = "up", speed_alt = 1.0,
			update_position = False)


	# return to original location
	# I am now in the top-right corner of the scanned area
	# move half the scaing area, down and left, from the top-right corner
	move(amount_az = -amount_step*steps/2, direction_az = "right", speed_az = config.speed_AZ,
		 amount_alt = -amount_step*steps/2, direction_alt = "up", speed_alt = config.speed_ALT,
		 update_position = False)
	#move(amount_az = -amount_total/2, direction_az = "right", speed_az = 1.0,
		 #amount_alt = -amount_total/2, direction_alt = "up", speed_alt = 1.0,
		 #update_position = False)
