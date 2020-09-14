
from time import sleep

# Raspberry Pi GPIO access
import RPi.GPIO as GPIO
#GPIO.setmode(GPIO.BCM)


import backup_location, config
from config import *

################## move 1 step at a time (or microstep)

# there is the option to update or not to update the location as you move

def up_1_step(update_position = True):
	GPIO.output(DIR_ALT, CCW_ALT)
	GPIO.output(STEP_ALT, GPIO.HIGH)
	sleep(config.delay_ALT)
	GPIO.output(STEP_ALT, GPIO.LOW)
	sleep(config.delay_ALT)

	if update_position == True:
		#global altitude
		config.altitude = config.altitude + 360.0 / config.steps_per_rotation_ALT
		config.altitude = config.altitude % 360.0
		backup_location.save_location()

def down_1_step(update_position = True):
	GPIO.output(DIR_ALT, CW_ALT)
	GPIO.output(STEP_ALT, GPIO.HIGH)
	sleep(config.delay_ALT)
	GPIO.output(STEP_ALT, GPIO.LOW)
	sleep(config.delay_ALT)

	if update_position == True:
		#global altitude
		config.altitude = config.altitude - 360.0 / sconfig.teps_per_rotation_ALT
		config.altitude = config.altitude % 360.0
		backup_location.save_location()

def right_1_step(update_position = True):
	GPIO.output(DIR_AZ, CW_ALT)
	GPIO.output(STEP_AZ, GPIO.HIGH)
	sleep(config.delay_AZ)
	GPIO.output(STEP_AZ, GPIO.LOW)
	sleep(config.delay_AZ)

	if update_position == True:
		#global azimuth
		config.azimuth = config.azimuth + 360.0 / config.steps_per_rotation_AZ
		config.azimuth = config.azimuth % 360.0
		backup_location.save_location()

def left_1_step(update_position = True):
	GPIO.output(DIR_AZ, CCW_ALT)
	GPIO.output(STEP_AZ, GPIO.HIGH)
	sleep(config.delay_AZ)
	GPIO.output(STEP_AZ, GPIO.LOW)
	sleep(config.delay_AZ)

	if update_position == True:
		#global azimuth
		config.azimuth = config.azimuth - 360.0 / config.steps_per_rotation_AZ
		config.azimuth = config.azimuth % 360.0
		backup_location.save_location()
