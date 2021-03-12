
## Settings file

# Print in color
# https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-python

class bcolors:
	NORMAL = 	'\033[0m'
	ENDC = 		'\033[0m'
	HEADER = 	'\033[95m'
	OKBLUE = 	'\033[94m'
	OKGREEN = 	'\033[92m'
	WARNING = 	'\033[93m'
	FAIL = 		'\033[91m'
	BOLD = 		'\033[1m'
	UNDERLINE = '\033[4m'

class TColors:
	normal = 			'\x1b[0m'
	red_on_black = 		'\x1b[0;31;40m'
	green_on_black = 	'\x1b[0;32;40m'
	orange_on_black = 	'\x1b[0;33;40m'
	blue_on_black = 	'\x1b[0;34;40m'
	purple_on_black = 	'\x1b[0;35;40m'
	yellow_on_black = 	'\x1b[0;36;40m'
	white_on_black = 	'\x1b[0;37;40m'
	italic = 			'\x1b[3;37;40m'
	bold = 				'\x1b[1;37;40m'
	undeline = 			'\x1b[4;37;40m'

# print(f"{bcolors.WARNING}Warning: No active frommets remain. Continue?{bcolors.ENDC}")
# print('\x1b[6;30;42m' + 'Success!' + '\x1b[0m')

# examples: https://i.stack.imgur.com/6otvY.png


# Raspberry Pi GPIO access
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


##### Microsteppg parameters, used next

# DRV8825 has 3 pins to control microstepping (full to 1/32).
# There are better drivers out there. The issue is the unequal step size.
MICROSTEP_RESOLUTION = {'Full': (0, 0, 0),
						'1/2': (1, 0, 0),
						'1/4': (0, 1, 0),
						'1/8': (1, 1, 0),
						'1/16': (0, 0, 1),
						'1/32': (1, 0, 1)}

# This is to update steps / revolution when changing microstepping
MICROSTEP_FACTOR = { 'Full': 1, '1/2': 2, '1/4': 4, '1/8': 8, '1/16': 16, '1/32': 32 }


##### Azimuth control

DIR_AZ = 17 #19 # Direction GPIO Pin
STEP_AZ = 27 #26 # Step GPIO Pin
CW_AZ = 1 # Clockwise Rotation
CCW_AZ = 0 # Counterclockwise Rotation

GPIO.setup(DIR_AZ, GPIO.OUT)
GPIO.setup(STEP_AZ, GPIO.OUT)
GPIO.output(DIR_AZ, CW_AZ)

microstep_az = '1/4'
SPR_BASE_AZ = 200*(360/36) # Steps per Revolution (360 / 1.8) * gear reduction
steps_per_rotation_AZ = SPR_BASE_AZ * MICROSTEP_FACTOR[ microstep_az ]

# MODE_AZ = (23, 24, 25) # Microstep Resolution GPIO Pins
MODE_AZ = (2, 3, 4) # Microstep Resolution GPIO Pins
GPIO.setup(MODE_AZ, GPIO.OUT)
GPIO.output(MODE_AZ, MICROSTEP_RESOLUTION[ microstep_az ])
#print ("Step size (Az): " + str( 360.0 / steps_per_rotation_AZ ) + " degrees. Microstepping: " + microstep_az + " .")

speed_AZ = 10.0 # deg / second

delay_AZ = 360.0 / (speed_AZ * steps_per_rotation_AZ * 2.0)
#print ("Time to complete 360 deg rotation (Az): " +  str(360.0/speed_AZ) + " seconds.")
#print ("Delay (Az): " + str(delay_AZ) + " seconds.\n")
#delay_AZ = 0.005 # failsafe value

azimuth = 0.0


##### ALtitude control

DIR_ALT = 21 # 16   # Direction GPIO Pin
STEP_ALT = 20 # 20  # Step GPIO Pin
CW_ALT = 0 # 1 	 # Clockwise Rotation
CCW_ALT = 1 # 0 	# Counterclockwise Rotation

GPIO.setup(DIR_ALT, GPIO.OUT)
GPIO.setup(STEP_ALT, GPIO.OUT)
GPIO.output(DIR_ALT, CW_ALT)

microstep_alt = '1/16'
SPR_BASE_ALT = 200*(180/36)   # Steps per Revolution (360 / 1.8) * gear reduction
steps_per_rotation_ALT = SPR_BASE_ALT * MICROSTEP_FACTOR[ microstep_alt ]

# MODE_ALT = (14, 15, 18)   # Microstep Resolution GPIO Pins
MODE_ALT = (6, 13, 19)   # Microstep Resolution GPIO Pins
GPIO.setup(MODE_ALT, GPIO.OUT)
GPIO.output(MODE_ALT, MICROSTEP_RESOLUTION[ microstep_alt ])
#print ("Step size (Alt): " + str( 360.0 / steps_per_rotation_ALT ) + " degrees. Microstepping: " + microstep_alt + " .")

speed_ALT = 10.0 # deg / second

delay_ALT = 360.0 / (speed_ALT * steps_per_rotation_ALT * 2.0)
#print ("Time to complete 360 deg rotation (Alt): " +  str(360.0/speed_ALT) + " seconds.")
#print ("Delay (Alt): " + str(delay_ALT) + " seconds.\n")
#delay_ALT = 0.005 # failsafe value

altitude = 0.0


################## other parameters

same = "0 0" # keep track of the last successfull searched location. TODO: fix the bug whih affects last_location_file
same_str = "" # print-ready version of same (only when same is a body)

# When in tracking mode, update every x seconds
track_refresh_interval = 20

# make a fake star, mostly for tracking arbitrary Az/Alt
fake_star = None # initialize with a proper value in ephem_wrapper.py

# obsevers: further defined later
observers_file = "observers.txt"
observer_name = "cluj" # default observer; has to be present in observers_file
observers, observer = None, None

# landmarks: further defined later
landmarks_file = "balcon_sud.landmakrs"
landmarks = []

# keep a record of the last known location (coordinates, body, time)
last_location_file = "/home/pi/last_location_file.txt"
