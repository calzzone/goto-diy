
#from time import sleep
#from getkey import getkey, keys
from datetime import datetime

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
from config import *

################## backup location

# whenever the current location changes, update a file just in case.
# one could reterive back the information and restart at the last kown location

def save_location():
	with open(config.last_location_file, "w") as f:
		line = str(config.azimuth) + ";" + str(config.altitude) + ";" + config.same + ";" + str(datetime.utcnow()) + "\n"
		f.write(line)

def recover_last_location():
	with open(lconfig.ast_location_file) as f:
		# Look at each line of the file
		for line in f:
			line=line.strip()

			# Skip comments
			if line.startswith('#'):
				continue

			pound = line.find("#")
			if pound >= 0:
				line = line[:pound]

			# Split the line apart.
			elements = line.split(";")
			break # 1 record only

	#global azimuth
	#global altitude
	#global same
	if len(elements) >= 2:
		config.azimuth = float(elements[0])
		config.altitude = float(elements[1])
		print ("Recovered last location: Az " + str(config.azimuth) + " Alt " + str(config.altitude) + ".")
	if len(elements) >= 3:
		if elements[2] != "":
			config.same = elements[2]
			print ("Recovered last successfull searched location: " + config.same + ".")
