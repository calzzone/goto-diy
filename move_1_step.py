
# Raspberry Pi GPIO access
# import RPi.GPIO as GPIO
# GPIO.setmode(GPIO.BCM)

################## move 1 step at a time (or microstep)

# there is the option to update or not to update the location as you move

def up_1_step(update_position = True):
	GPIO.output(DIR_ALT, CCW_ALT)
	GPIO.output(STEP_ALT, GPIO.HIGH)
	sleep(delay_ALT)
	GPIO.output(STEP_ALT, GPIO.LOW)
	sleep(delay_ALT)

	if update_position == True:
		global altitude
		altitude = altitude + 360.0 / SPR_ALT
		altitude = altitude % 360.0
		save_location()

def down_1_step(update_position = True):
	GPIO.output(DIR_ALT, CW_ALT)
	GPIO.output(STEP_ALT, GPIO.HIGH)
	sleep(delay_ALT)
	GPIO.output(STEP_ALT, GPIO.LOW)
	sleep(delay_ALT)

	if update_position == True:
		global altitude
		altitude = altitude - 360.0 / SPR_ALT
		altitude = altitude % 360.0
		save_location()

def right_1_step(update_position = True):
	GPIO.output(DIR_AZ, CW_ALT)
	GPIO.output(STEP_AZ, GPIO.HIGH)
	sleep(delay_AZ)
	GPIO.output(STEP_AZ, GPIO.LOW)
	sleep(delay_AZ)

	if update_position == True:
		global azimuth
		azimuth = azimuth + 360.0 / SPR_AZ
		azimuth = azimuth % 360.0
		save_location()

def left_1_step(update_position = True):
	GPIO.output(DIR_AZ, CCW_ALT)
	GPIO.output(STEP_AZ, GPIO.HIGH)
	sleep(delay_AZ)
	GPIO.output(STEP_AZ, GPIO.LOW)
	sleep(delay_AZ)

	if update_position == True:
		global azimuth
		azimuth = azimuth - 360.0 / SPR_AZ
		azimuth = azimuth % 360.0
		save_location()
