
# Raspberry Pi GPIO access
# import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)


import move_function, config

################## move 1 degree

def up_1(update_position = True):
	move_function.move(amount_alt = 1.0, direction_alt = "up", speed_alt = config.SPEED_ALT, min_steps_alt = 0,
		update_position = update_position)

def down_1(update_position = True):
	move_function.move(amount_alt = 1.0, direction_alt = "down", speed_alt = config.SPEED_ALT, min_steps_alt = 0,
		update_position = update_position)

def right_1(update_position = True):
	move_function.move(amount_az = 1.0, direction_az = "right", speed_az = config.SPEED_AZ, min_steps_az = 0,
		update_position = update_position)

def left_1(update_position = True):
	move_function.move(amount_az = 1.0, direction_az = "left", speed_az = config.SPEED_AZ, min_steps_az = 0,
		update_position = update_position)
