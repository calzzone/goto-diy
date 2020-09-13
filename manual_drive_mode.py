
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

from set_functions import *
from backup_location import *
from move_function import *
from move_1_step import *
from move_1_deg import *
################## manual drive mode

def manual_drive():
	print("Mamual drive with arrows to move slowly and awsd to move 1 deg at a time.")
	print("c to cancel, ? / ! to get status.")
	while(True):
		key = getkey()
		if key == keys.UP: up_1_step(update_position = True)
		elif key == keys.DOWN: down_1_step(update_position = True)
		elif key == keys.LEFT: left_1_step(update_position = True)
		elif key == keys.RIGHT: right_1_step(update_position = True)
		elif key == 'w': up_1(update_position = True)
		elif key == 's': down_1(update_position = True)
		elif key == 'a': left_1(update_position = True)
		elif key == 'd': right_1(update_position = True)
		elif key == '?': print_location()
		elif key == '!': print_status()
		elif key == 'c': break
		#else: print(key)
