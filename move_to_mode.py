
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




################## move

# move a specific arc at a specified speed
# currently, only called from within go_to_location(), but this will probably change
# TODO?: maybe move both axes at the same time? It looks cooler, but not really worth it.


# TODO: some acceletaion and deceleration profiles, probably also manipulating microstepping to increase spped, accuracy, noise and vibrations

# ramp-up, stall, then ramp-down
ramp_az_threshold = 30 # only ramp if you have to move more than 50 steps
ramp_alt_threshold = 30
ramp_az_rate = 1 - 0.005 # 0.5% faster each step
ramp_alt_rate = 1 - 0.005
ramp_az_max_speed_factor = 5 # ramp up until 4 times faster than base speed
ramp_alt_max_speed_factor = 5

# not called directly by the user
def move(amount_az = 0.0, direction_az = "right", speed_az = 10.0, min_steps_az = 2,
		amount_alt = 0.0, direction_alt = "up", speed_alt = 10.0, min_steps_alt = 2,
		update_position = True):
	#print("Debug move:", amount_az, direction_az, amount_alt, direction_alt)

	if amount_az < 0: # revert direction
		if direction_az == "right": direction_az = "left"
		else: direction_az == "left"
		amount_az = abs(amount_az)

	global azimuth
	step_count_az =  int(round(amount_az *  SPR_AZ  / 360.0))
	if step_count_az >= min_steps_az:
		if direction_az == "right":  GPIO.output(DIR_AZ, CW_AZ)
		else: GPIO.output(DIR_AZ, CCW_AZ)
		delay_az = 360.0 / (speed_az * SPR_AZ * 2.0)
		print ("Az will move " + direction_az + " " + str(step_count_az) + " steps, at a speed of " + str(speed_az) + " degrees / second")

		temp_min_delay_az = delay_az / ramp_az_max_speed_factor

		for x in range(int(step_count_az)):

			# ramp-up, stall, then ramp-down:
			if step_count_az > ramp_az_threshold:
				if x < step_count_az / 2: # ramp-up or stall
					temp_delay_az = max(temp_min_delay_az, delay_az * ramp_az_rate**x) # ! do not below min delay
				else: # ramp-down
					y = step_count_az - x
					temp_delay_az = max(temp_min_delay_az, delay_az * ramp_az_rate**y) # ! do not below min delay
			else: temp_delay_az = delay_az

			#print (round(temp_delay_az*1000, 3))

			GPIO.output(STEP_AZ, GPIO.HIGH)
			sleep(temp_delay_az)
			GPIO.output(STEP_AZ, GPIO.LOW)
			sleep(temp_delay_az)

			if update_position:
				if direction_az == "right":  azimuth = azimuth + 360.0 / SPR_AZ
				else: azimuth = azimuth - 360.0 / SPR_AZ
				azimuth = azimuth % 360.0

	###
	if amount_alt < 0: # revert direction
		if direction_alt == "up": direction_alt = "down"
		else: direction_alt == "up"
		amount_alt = abs(amount_alt)

	global altitude
	step_count_alt =  int(round(amount_alt *  SPR_ALT  / 360.0))
	#print("step count alt: " + str(step_count_alt))
	if step_count_alt >= min_steps_alt:
		if direction_alt == "up":  GPIO.output(DIR_ALT, CCW_ALT)
		else: GPIO.output(DIR_ALT, CW_ALT)
		delay_alt = 360.0 / (speed_alt * SPR_ALT * 2.0)
		print ("Alt will move " + direction_alt + " " + str(step_count_alt) + " steps, at a speed of " + str(speed_alt) + " degrees / second.")

		temp_min_delay_alt = delay_alt / ramp_alt_max_speed_factor

		for x in range(int(step_count_alt)):
			if step_count_alt > ramp_alt_threshold:
				if x < step_count_alt / 2: # ramp-up or stall
					temp_delay_alt = max(temp_min_delay_alt, delay_alt * ramp_alt_rate**x) # ! do not below min delay
				else: # ramp-down
					y = step_count_alt - x
					temp_delay_alt = max(temp_min_delay_alt, delay_alt * ramp_alt_rate**y) # ! do not below min delay
			else: temp_delay_alt = delay_alt

			GPIO.output(STEP_ALT, GPIO.HIGH)
			sleep(temp_delay_alt)
			GPIO.output(STEP_ALT, GPIO.LOW)
			sleep(temp_delay_alt)

			if update_position:
				if direction_alt == "up":  altitude = altitude + 360.0 / SPR_ALT
				else: altitude = altitude - 360.0 / SPR_ALT
				altitude = altitude % 360.0

	save_location()
