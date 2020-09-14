
#from time import sleep
#from getkey import getkey, keys
#from datetime import datetime

#import os
#print (os.path.abspath(os.getcwd()))

#import signal
#import sys
#from threading import Timer
#from readchar import readkey

#import string
#import math

#import ephem
#from ephem import *

# global variables
import config
#from config import *

#import backup_location # for save_location() in set_location()

################## print info


def print_location():
	print("Curent Az: " + str(config.azimuth) + ", Alt: " + str(config.altitude))

def print_status():
	print_location()
	if config.same != "": print ("Last successfull searched body:" + config.same)

	print("Speed Az: " + str(config.speed_AZ) + ", Alt: " + str(config.speed_ALT))
	print ("Time to complete 0 to 360 deg rotation (Az): " +  str(360.0 / config.speed_AZ) + " seconds.")
	print ("delay (Az): " + str(config.delay_AZ) + " seconds.")

	print ("Time to complete 0 to 90 deg rotation (Alt): " +  str(90.0 / config.speed_ALT) + " seconds.")
	print ("delay (Alt): " + str(config.delay_ALT) + " seconds.")

	print("Microstepping Az: " + str(config.microstep_az) + ", Alt: " + str(config.microstep_alt))

	print("Track refresh interval: " + str(config.track_refresh_interval) + " seconds." )
