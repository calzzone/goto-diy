### This is the main code file f my telescope control software.

# https://git.nexlab.net/astronomy/skylived/tree/bd59190026d9d95b39983f8a0106a7e17023aee8/DecraDB/xephemdb
# https://github.com/Alex-Broughton/StarAtlas

# Raspberry Pi GPIO access
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Global variables
import config
from config import *

# Welcome message
print ("\n\x1b[1;37;42m ====== DIY GoTo Telesope Control ===== " + TColors.normal + " \n")


from load_observers import *
config.observers = gather_observers(config.observers_file)
config.observer, config.observer_name = set_observer(config.observer_name)

from load_landmarks import *
config.landmarks = gather_landmarks(config.landmarks_file)

from backup_location import * # CRITICAL: before set_functions
from set_functions import * # CRITICAL: after backup_location

from ephem_wrapper import * # here: for printing names of stars

#from move_function import * # not directly
#from move_1_step import * # not directly
#from move_1_deg import * # not directly

# Operating modes
from track_mode import *
from go_to_mode import *
from manual_drive_mode import *
from scan_sky_mode import *





##################

def quit_nicely():
	GPIO.cleanup()
	print (TColors.italic + "\nGood riddance!\n" + TColors.normal)


def show_options():
	print (TColors.bold + "\nAvailable options:" + TColors.normal)
	print (TColors.orange_on_black + "0:" + TColors.normal + " Quit nicely")
	print (TColors.orange_on_black + "1-4:" + TColors.blue_on_black + " Operating modes: " + TColors.normal + "track " + TColors.orange_on_black + "(1)" + TColors.normal + ", move " + TColors.orange_on_black + "(2)" + TColors.normal + ", manual drive " + TColors.orange_on_black + "(3)" + TColors.normal + " , scan sky area " + TColors.orange_on_black + "(4)" + TColors.normal)
	print (TColors.orange_on_black + "5-9:" + TColors.blue_on_black + " Set: " + TColors.normal + "speed " + TColors.orange_on_black + "(5)" + TColors.normal + ", microstepping " + TColors.orange_on_black + "(6)" + TColors.normal + ", track refresh interval " + TColors.orange_on_black + "(7)" + TColors.normal + ", observer " + TColors.orange_on_black + "(8)" + TColors.normal + ", current coordinates " + TColors.orange_on_black + "(9)" + TColors.normal)
	print (TColors.orange_on_black + "10:" + TColors.normal + " Recover last recoded coordinates")
	print (TColors.orange_on_black + "18 19 20:" + TColors.blue_on_black + " Print: " + TColors.normal + "observer " + TColors.orange_on_black + "(18)" + TColors.normal + ", current coordinates " + TColors.orange_on_black + "(19)" + TColors.normal + ", status " + TColors.orange_on_black + "(20)" + TColors.normal)
	print (TColors.orange_on_black + "21-23:" + TColors.blue_on_black + " Print: " + TColors.normal + "named stars " + TColors.orange_on_black + "(21)" + TColors.normal + ", all available stars in YBS " + TColors.orange_on_black + "(22)" + TColors.normal + ", landmakrs " + TColors.orange_on_black + "(23)" + TColors.normal)
	print (TColors.orange_on_black + "31:" + TColors.normal + " Make fake star")

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
	option = int(input(TColors.italic + "What is my purpose? " + TColors.normal))
	print('\n')
	while option != 0:
		switch_main(option)
		show_options()
		option = int(input(TColors.italic + "What is my purpose? " + TColors.normal))
		print('\n')

	#GPIO.cleanup()
	quit_nicely()

if __name__ == '__main__':
	main()

#GPIO.cleanup()
#quit_nicely()
