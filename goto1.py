# https://git.nexlab.net/astronomy/skylived/tree/bd59190026d9d95b39983f8a0106a7e17023aee8/DecraDB/xephemdb
# https://github.com/Alex-Broughton/StarAtlas

from time import sleep
from getkey import getkey, keys
from datetime import datetime

import os
import signal
import sys
from threading import Timer
from readchar import readkey

import string
import math

import ephem
from ephem import *	  

# Raspberry Pi GPIO access
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

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

track_refresh_interval = 10.0



##### ALtitude control

DIR_ALT = 16   # Direction GPIO Pin
STEP_ALT = 20  # Step GPIO Pin

CW_ALT = 1	 # Clockwise Rotation
CCW_ALT = 0	# Counterclockwise Rotation

GPIO.setup(DIR_ALT, GPIO.OUT) 
GPIO.setup(STEP_ALT, GPIO.OUT)
GPIO.output(DIR_ALT, CW_ALT)

microstep_alt = '1/16'
SPR_BASE_ALT = 200*(180/36)   # Steps per Revolution (360 / 1.8)
SPR_ALT = SPR_BASE_ALT * MICROSTEP_FACTOR[ microstep_alt ]

MODE_ALT = (14, 15, 18)   # Microstep Resolution GPIO Pins
GPIO.setup(MODE_ALT, GPIO.OUT)
GPIO.output(MODE_ALT, MICROSTEP_RESOLUTION[ microstep_alt ])
print ("Step size (Alt): " + str( 360.0 / SPR_ALT ) + " degrees. Microstepping: " + microstep_alt + " .")

#DURATION_ALT = 60.0
SPEED_ALT = 10.0 # deg / second

delay_ALT = 360.0 / (SPEED_ALT * SPR_ALT * 2.0)
print ("Time to complete 360 deg rotation (Alt): " +  str(360.0/SPEED_ALT) + " seconds.")
print ("Delay (Alt): " + str(delay_ALT) + " seconds.\n")
#delay_ALT = 0.005

ALT = 0.0
#altitude = ALT * (SPR_ALT/4.0 ) / 90.0
altitude = 0.0



##### Azimuth control

DIR_AZ = 19 # Direction GPIO Pin
STEP_AZ = 26 # Step GPIO Pin
CW_AZ = 1 # Clockwise Rotation
CCW_AZ = 0 # Counterclockwise Rotation

GPIO.setup(DIR_AZ, GPIO.OUT) 
GPIO.setup(STEP_AZ, GPIO.OUT)
GPIO.output(DIR_AZ, CW_AZ)

microstep_az = '1/8'
SPR_BASE_AZ = 200*(360/36) # Steps per Revolution (360 / 1.8)
SPR_AZ = SPR_BASE_AZ * MICROSTEP_FACTOR[ microstep_az ]

MODE_AZ = (23, 24, 25) # Microstep Resolution GPIO Pins
GPIO.setup(MODE_AZ, GPIO.OUT)
GPIO.output(MODE_AZ, MICROSTEP_RESOLUTION[ microstep_az ])
print ("Step size (Az): " + str( 360.0 / SPR_AZ ) + " degrees. Microstepping: " + microstep_az + " .")

SPEED_AZ = 10.0 # deg / second

delay_AZ = 360.0 / (SPEED_AZ * SPR_AZ * 2.0)
print ("Time to complete 360 deg rotation (Az): " +  str(360.0/SPEED_AZ) + " seconds.")
print ("Delay (Az): " + str(delay_AZ) + " seconds.\n")
#delay_AZ = 0.005

AZ = 0.0
#azimuth = AZ * (SPR_AZ/4.0 ) / 90.0
azimuth = 0.0




################## other parameters

same = "0 0" # keep track of the last successfull searched location. TODO: fix the bug whih affects last_location_file
same_str = "" # print-ready version of same (only when same is a body)

last_location_file = "last_location_file.txt" # keep a record of the last known location (coordinates, body, time)


################## ephem

##### observers (observing location on the earth)
# ephem knows a list of cities, but it's too small.
# TODO: use some online thing to get gps coordinates, elevation and even pressure and temperature

observers_file = "observers.txt"

# reads observers_file and returns a dictionary of observer_names : ephem.Observer pairs
def gather_observers():
	
	observers_lines = open(observers_file, "r").readlines()
	observers = {}
	
	for line in observers_lines:
		line=line.strip()
	
		# Skip comments
		if line.startswith('#'):
			continue
		
		pound = line.find("#")
		if pound >= 0:
			line = line[:pound]
		
		# new observer
		elements = line.split(";") 
		
		observer = ephem.Observer()
		observer.lat, observer.lon = elements[1], elements[2]
		
		if len(elements) >= 3:
			observer.elevation = elements[3]
		
		if len(elements) >= 4:
			observer.pressure, observer.temp = elements[4], elements[5] 
		else: 
			observer.pressure, observer.temp = 1013, 15# stellarium settings
		
		observers[elements[0]] = observer
	
	return (observers)

observers = gather_observers()

def set_observer(new_observer):
	while True:
		if new_observer is None:
			new_observer = input("Type the name of the observer location as defined in " + observers_file + " or 'c' to cancel: ")
		
		if new_observer == "c": return ()
		elif new_observer in observers.keys():
			#observer = observers
			return (observers[new_observer], new_observer)



observer_name == "cluj"
observer = set_observer(observer_name)


#marisel = ephem.Observer()
#marisel.lat, marisel.lon = '46.680821', '23.152553'
#marisel.elevation = 1050
#marisel.pressure, marisel.temp = 1013, 15 # stellarium settings

#cluj = ephem.Observer()
#cluj.lat, cluj.lon = '46.7424895', '23.5650096'
#cluj.elevation = 850
#cluj.pressure, cluj.temp = 1013, 15 # stellarium settings
##cluj.horizon="0:34"
##cluj.date = '2020/7/17 12:52'
#
#observer = cluj

def get_observer():
	print ("Current observing location: " + observer_name + ":")
	print ("Lat: " + str(observer.lat) + "Lon: " + str(observer.lon) + 
		   "Elevtion: " + str(observer.elevation) + "\n" +
		   "Pressure: " + str(observer.pressure) + "Temp: " + str(observer.temp) )
	
###### available named bodies

# named stars built into ephem
list_of_stars = open("ephem_stars.txt", "r").readlines()
list_of_stars = [star[:-1].lower() for star in list_of_stars]

# named stars in an other catalog
list_of_stars2 = open("YBS.txt", "r").readlines()
list_of_stars2 = [star[:-1].lower() for star in list_of_stars2]

# there is a way to infer what kind of celestial body is one
def describe_body( subfields ):
	# Map the edb format type-subfield codes to presentable text
	if subfields[0] == 'P':
		return "planet"
	if subfields[0] == 'E':
		return "satellite"
	if subfields[0] in 'ehp':
		return "planetoid"
		
	FIXED_BODY_MAP = {
		'A' : "cluster of galaxies",
		'B' : "binary star",
		'C' : "globular cluster",
		'D' : "visual double star",
		'F' : "diffuse nebula",
		'G' : "spiral galaxy",
		'H' : "spherical galaxy",
		'J' : "radio object",
		'K' : "dark nebula",
		'L' : "pulsar",
		'M' : "multiple star",
		'N' : "bright nebula",
		'O' : "open cluster",
		'P' : "planetary nebula",
		'Q' : "quasar",
		'R' : "supernova remnant",
		'S' : "star",
		'T' : "stellar object",
		'U' : "nebulous cluster",
		'V' : "variable star",
		'Y' : "supernova",
		"?" : "unknown / uspecified" }			
		
	if subfields[0] == 'f':
		return FIXED_BODY_MAP[subfields[1]]  
		
	return "?"

# reads an arbitrary edb file
def read_database( filename ):
	# Read a set of bodies from an EDB file. 
	bodies = []
	desc = {}   
	
	# Read the file.
	with open(filename) as f:
		# Look at each line of the file
		for line in f:
			line=line.strip()
		
			# Skip comments
			if line.startswith('#'):
				continue	
			
			# Skip malformed lines
			if "," not in line:
				continue			  
			
			# describe body
			#line = line.replace(",f,", ",f|?,") # temporary precausion to make describe_body() shut up; most are already done
			# Split the line apart.
			elements = line.split(",") 
			# Extract the name
			name = elements[0]
			# Extract the type fields
			subfields = elements[1].split('|') 
			# Map those to a description
			desc = describe_body(subfields)  
			
			# Give the whole line to pyephem; # revent the previous "fix"
			body = ephem.readdb(line.replace(",f|?,", ",f,"))
			
			bodies.append( (name, desc,body) )
		
	return bodies

# wrapper around ephem.compute(); there is a more "pattern-y" way to do it but why bother...
# given a celestial body and an observer location (both ephem classes), get current coordinates (Az, Alt)
def compute(thing, observer):
	now = datetime.utcnow()
	observer.date = now
	thing.compute(observer)
	print("Angle Az Alt:", thing.az, thing.alt)
	return(thing.az*180/math.pi, thing.alt*180/math.pi)
	
	#return(#ephem.degrees(thing.az), ephem.degrees(thing.alt), 
	#	thing.az*180/math.pi, thing.alt*180/math.pi)


################## ephem: search

# search body name in a list of ephem bodies
# TODO: use a dictionary, dumbass
def find_body_by_name(name, catalog):
	for body in catalog:
		if body[0] == name:
			print(body)
			return body[2]
	return (None)

# only called from inside a higer level search function
# look for and get coordinates of an arbitrary "target" named body
# TODO: use a dictionary, dumbass
# TODO: have better flexibility when searching

def search_0(target):
	if target.lower() == "sun": thing = ephem.Sun()
	elif target.lower() == "moon": thing = ephem.Moon()
	elif target.lower() == "mercury": thing = ephem.Mercury()
	elif target.lower() == "venus": thing = ephem.Venus()
	elif target.lower() == "mars": thing = ephem.Mars()
	elif target.lower() == "jupiter": thing = ephem.Jupiter()
	elif target.lower() == "saturn": thing = ephem.Saturn()
	elif target.lower() == "uranus": thing = ephem.Uranus()
	elif target.lower() == "neptune": thing = ephem.Neptune()
	elif target.lower()[0] == 'm' and target[1:].isnumeric() and int(target[1:]) <= 110:
		messier = read_database("Messier.edb")
		name = "M" + target[1:].strip()
		thing = find_body_by_name(name, messier)
	elif target.lower().startswith('ic'): 
		ic = read_database("IC.edb")
		name = "IC" + target[2:].strip()
		thing = find_body_by_name(name, ic)
	elif target.lower().startswith('ngc'): 
		ngc = read_database("NGC.edb")
		name = "NGC" + target[3:].strip()
		thing = find_body_by_name(name, ngc)
	elif target.lower().startswith('ugc'): # also UGCA 
		ugc = read_database("UGC.edb")
		name = "UGC" + target[3:].strip()
		thing = find_body_by_name(name, ugc)
	elif target.lower().endswith("xxx") or target.lower() == "neowise": 
		neowise = read_database("neowise.edb")
		thing = find_body_by_name("C/2020 F3 (NEOWISE)", neowise)
	elif target.lower() in list_of_stars:
		thing = ephem.star(string.capwords(target))
	elif target.lower().strip() in list_of_stars2:
		YBS = read_database("YBS.edb")
		star = list_of_stars2.index( target.lower().strip() )
		print("Other stars catalog: " + YBS[star][0])
		thing = YBS[star][2]
	else: return(None)

	if thing is None: return (None)
	
	return(compute(thing, observer))

# actual search function called from the UI
def search():
	global same # TODO: the error!
	global same_str
	
	print("List of available stars:")
	print(list_of_stars) # TODO: print more
	
	while True:
		same_str_builder = ": " + same_str if same_str != "" else ""
		location = input("Location (`home`, Az [0-360) Alt [0-90 deg], common name, 'same`" + same_str_builder + " or 'c' to cancel): ")
		if location == "same": location = same
		if location == "home": location = "0 0"
		elif location == 'c': return(None, None)
		temp = location
		
		LS = location.split()
		if len(LS) == 2 and LS[0].replace('.', '').isnumeric() and LS[1].replace('.', '').isnumeric():
			location = [float(x) for x in LS]
			# TODO (maybe) check values are valid angles
			same_str = "Az " + str(round(location[0], 3)) + " Alt " + str(round(location[1], 3))
		else:
			location = search_0(location)
			if location is None:
				print("Not found. Try again. ")
				continue
			if location[1] < 0: # maybe don't look below horizon...
				alert = input("! Below horizon! Are you sure? [*/yes] ")
				if alert != "yes": 
					continue
			same_str = ""
			
		az, alt = location[0], location[1]
		print("Arbitrary location Az: " + str(az) + ", Alt: " + str(alt))
		
		same = temp
		return (az, alt)


################## setup functions

def set_speed():
	global delay_ALT
	global SPEED_ALT
	global delay_AZ
	global SPEED_AZ

	SPEED_AZ, SPEED_ALT = map(float, input("Speed for Az Alt (deg/second): ").split()) 

	delay_AZ = 360.0 / (SPEED_AZ * SPR_AZ * 2.0)
	print ("Time to complete 0 to 360 deg rotation (Az): " +  str(360.0 / SPEED_AZ) + " seconds.")
	print ("delay (Az): " + str(delay_AZ) + " seconds.")

	delay_ALT = 360.0 / (SPEED_ALT * SPR_ALT * 2.0)
	print ("Time to complete 0 to 90 deg rotation (Alt): " +  str(90.0 / SPEED_ALT) + " seconds.")
	print ("delay (Alt): " + str(delay_ALT) + " seconds.")

# TODO: when micros changes, does location stay the same?
def set_microstepping():
	global microstep_az
	global microstep_alt
	global SPR_AZ
	global SPR_ALT

	print("Enable / disable microstepping in Az and Alt axes")
	microstep_az, microstep_alt = input("Az Alt microstepping resolution ( Full, 1/2-1/32 ): ").split()

	GPIO.output(MODE_AZ, MICROSTEP_RESOLUTION[microstep_az])
	SPR_AZ = SPR_BASE_AZ * MICROSTEP_FACTOR[ microstep_az ]

	GPIO.output(MODE_ALT, MICROSTEP_RESOLUTION[microstep_alt])
	SPR_ALT = SPR_BASE_ALT * MICROSTEP_FACTOR[ microstep_alt ]

	print ("Step size (Az): " + str( 360.0 / SPR_AZ ) + " degrees. Microstepping: " + microstep_az + " .")
	print ("Step size (Alt): " + str( 360.0 / SPR_ALT ) + " degrees. Microstepping: " + microstep_alt + " .")


# when in tracking mode, update every ... seconds
def set_track_refresh_interval():
	global track_refresh_interval
	track_refresh_interval = float(input("Tracking refresh interval (seconds): "))

################## backup location

# whenever the current location changes, update a file just in case. 
# one could reterive back the information and restart at the last kown location

def recover_last_location():
	with open(last_location_file) as f:
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
	
	global azimuth
	global altitude
	global same
	if len(elements) >= 2:
		azimuth = float(elements[0])
		altitude = float(elements[1])
		print ("Recovered last location: Az " + str(azimuth) + " Alt " + str(altitude) + ".")
	if len(elements) >= 3:
		if elements[2] != "":
			same = elements[2]
			print ("Recovered last successfull searched location: " + same + ".")
		
	
def save_location():
	with open(last_location_file, "w") as f:
		line = str(azimuth) + ";" + str(altitude) + ";" + same + ";" + str(datetime.utcnow()) + "\n"
		f.write(line)


################## set curent location

def set_location():
	global azimuth
	global altitude

	#azimuth, altitude = map(float, input("Current Az Alt: ").split()) 
	new_azimuth, new_altitude = search()
	if (new_azimuth == None or new_altitude == None):
		return()
	
	azimuth  = new_azimuth % 360.0	
	altitude = new_altitude  % 360.0
	
	save_location()


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




################## move 1 degree

def up_1(update_position = True):
	step_count_alt = int(round(1 * SPR_ALT / 360.0))
	# print (step_count_alt)
	GPIO.output(DIR_ALT, CCW_ALT)
	for x in range(step_count_alt):
		GPIO.output(STEP_ALT, GPIO.HIGH)
		sleep(delay_ALT)
		GPIO.output(STEP_ALT, GPIO.LOW)
		sleep(delay_ALT)

		if update_position == True: 
			global altitude
			altitude = altitude + 360.0 / SPR_ALT
			altitude = altitude % 360.0
			save_location()

def down_1(update_position = True):	
	step_count_alt = int(round(1 *  SPR_ALT / 360.0))
	GPIO.output(DIR_ALT, CW_ALT)
	for x in range(step_count_alt):
		GPIO.output(STEP_ALT, GPIO.HIGH)
		sleep(delay_ALT)  
		GPIO.output(STEP_ALT, GPIO.LOW)
		sleep(delay_ALT)

		if update_position == True: 
			global altitude
			altitude = altitude - 360.0 / SPR_ALT
			altitude = altitude % 360.0
			save_location()



def right_1(update_position = True):
	step_count_az = int(round(SPR_AZ / 360.0))
	GPIO.output(DIR_AZ, CW_AZ)
	for x in range(step_count_az):
		GPIO.output(STEP_AZ, GPIO.HIGH)
		sleep(delay_AZ)
		GPIO.output(STEP_AZ, GPIO.LOW)
		sleep(delay_AZ)
		
		if update_position == True: 
			global azimuth
			azimuth = azimuth + 360.0 / SPR_AZ
			azimuth = azimuth % 360.0
			save_location()


def left_1(update_position = True):
	step_count_az = int(round(SPR_AZ / 360.0))
	GPIO.output(DIR_AZ, CCW_AZ)
	for x in range(step_count_az):
		GPIO.output(STEP_AZ, GPIO.HIGH)
		sleep(delay_AZ)
		GPIO.output(STEP_AZ, GPIO.LOW)
		sleep(delay_AZ)
		
		if update_position == True: 
			global azimuth
			azimuth = azimuth - 360.0 / SPR_AZ
			azimuth = azimuth % 360.0
			save_location()


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
		elif key == '?': get_location()
		elif key == '!': get_status()
		elif key == 'c': break
		#else: print(key)


################## move

# move a specific arc at a specified speed
# currently, only called from within go_to_location(), but this will probably change
# TODO?: maybe move both axes at the same time? It looks cooler, but not really worth it.
# TODO: some acceletaion and deceleration profiles, probably also manipulating microstepping to increase spped, accuracy, noise and vibrations

# not called directly by the user
def move(amount_az = 0.0, direction_az = "right", speed_az = 1.0, amount_alt = 0.0, direction_alt = "up", speed_alt = 1.0):
	#print("Debug move:", amount_az, direction_az, amount_alt, direction_alt)

	global azimuth
	step_count_az =  int(round(amount_az *  SPR_AZ  / 360.0)) 
	if step_count_az > 0:
		if direction_az == "right":  GPIO.output(DIR_AZ, CW_AZ)
		else: GPIO.output(DIR_AZ, CCW_AZ)  
		delay_az = 360.0 / (speed_az * SPR_AZ * 2.0)
		print ("Az will move " + direction_az + " " + str(step_count_az) + " steps, at a speed of " + str(speed_az) + " degrees / second")
		
		for x in range(int(step_count_az)):
			GPIO.output(STEP_AZ, GPIO.HIGH)
			sleep(delay_az)
			GPIO.output(STEP_AZ, GPIO.LOW)
			sleep(delay_az)

			if direction_az == "right":  azimuth = azimuth + 360.0 / SPR_AZ
			else: azimuth = azimuth - 360.0 / SPR_AZ
			azimuth = azimuth % 360.0

	###

	global altitude
	step_count_alt =  int(round(amount_alt *  SPR_ALT  / 360.0))
	if step_count_alt > 0:
		if direction_alt == "up":  GPIO.output(DIR_ALT, CCW_ALT)
		else: GPIO.output(DIR_ALT, CW_ALT)  
		delay_alt = 360.0 / (speed_alt * SPR_ALT * 2.0)
		print ("Alt will move " + direction_alt + " " + str(step_count_alt) + " steps, at a speed of " + str(speed_alt) + " degrees / second.")
		
		for x in range(int(step_count_alt)):
			GPIO.output(STEP_ALT, GPIO.HIGH)
			sleep(delay_alt)
			GPIO.output(STEP_ALT, GPIO.LOW)
			sleep(delay_alt)

			if direction_alt == "up":  altitude = altitude + 360.0 / SPR_ALT
			else: altitude = altitude - 360.0 / SPR_ALT
			altitude = altitude % 360.0
			
	save_location()


# let the user specify a location (coordinates or named body) and go there
def go_to_location():
	target_az =  -1
	target_alt = -1
	while target_az < 0 or target_az >= 360 or target_alt < 0 or target_alt > 90:
		#target_az, target_alt = map(float, input("Target Az [0-360) Alt [0-90 deg]: (-360 to cancel) ").split())
		target_az, target_alt = search()
		if (target_alt == None or target_az == None):
			return()
		if (target_alt == altitude and target_az == azimuth):
			return()

	if azimuth != target_az:
		print ("Will move Az from " + str(azimuth) + " to " + str(target_az))
	if altitude != target_alt:
		print ("Will move Alt from " + str(altitude) + " to " + str(target_alt))
	
#	delta_az = abs(target_az - azimuth)
#	delta_az %= 360.0
#	delta_az = 180.0 - abs(delta_az - 180.0)
#	if (azimuth + delta_az) % 360.0 == target_az:
#		direction_az = "right"
#	else: direction_az = "left"

	Az = azimuth + 360.0
	TAz = target_az + 360.0
	delta_az_right = (TAz - Az) % 360.0
	delta_az_left  = (Az - TAz) % 360.0
	
	delta_az = min(delta_az_right, delta_az_left)
	direction_az = ("left", "right")[delta_az_right < delta_az_left] 
	
	if altitude > 180: delta_alt = target_alt - altitude + 360 # TODO: should not happen under regular usage!
	else: delta_alt = target_alt - altitude
	direction_alt = ("down", "up")[delta_alt > 0.0]

	move(amount_az = delta_az, direction_az = direction_az, speed_az = SPEED_AZ, 
		amount_alt = abs(delta_alt), direction_alt = direction_alt, speed_alt = SPEED_ALT)
	

################## track

# in tracking moe,teh user searches for a body, the program goes there and then recomputes its coordonates and moves accordingly every few seconds
# meanwhile, the user can manually fine-tune the position of the telescope so the actual position coresponds to the position the software thinks it should be pointing to

# accept keyboard input (c or tuning directions) while waiting between moves
# the regular getkey method is not good because it does not expire after a set timeout
def wait_for(timeout):
	pid = os.getpid()
	sig = signal.SIGINT
	timer = Timer(timeout, lambda: os.kill(pid, sig))
	print(f"Auto-tracking with maual control. Press 'c' to cancel, ? / ! to get stauts. Next move in {timeout} seconds. ")
	timer.start()  # spawn a worker thread to interrupt us later
	#paused = False
	while True:
		key = readkey()
		#print(f"received {k!r}")
		if key == 'c':
			print("Exiting tracking mode...")
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
		elif key == '?': get_location()
		elif key == '!': get_status()
		elif key == keys.UP: up_1_step(update_position = False)
		elif key == keys.DOWN: down_1_step(update_position = False)
		elif key == keys.LEFT: left_1_step(update_position = False) #
		elif key == keys.RIGHT: right_1_step(update_position = False) #
		elif key == 'w': up_1(update_position = False)
		elif key == 's': down_1(update_position = False)
		elif key == 'a': left_1(update_position = False) #
		elif key == 'd': right_1(update_position = False) 
		
	#return (None)

def track():
	# step 1: search for something to track (TODO track coordinates)
	found = False
	while not found:
		same_str_builder = ": " + same_str if same_str != "" else ""
		location = input("Location (common name, 'same`" + same_str_builder + " or 'c' to cancel): ")
		
		if location == 'c': return ()	
	
		if location == "same": 
			location = same
		
		location_coord = search_0(location)
		
		if location_coord is None:
			print("Not found. Try again. ")
			continue
		
		if location_coord[0] < 0 or location_coord[0] >= 360 or location_coord[1] < 0 or location_coord[1] > 90:
			print("Outside valid and / or trackable ranges. Try again. ")
			continue
		
		found = True
	
	target_az, target_alt = location_coord[0], location_coord[1]
	
	
	# step 2: track: move, wait for ... seconds while accepting keybord input, search again
	while not (target_az < 0 or target_az >= 360 or target_alt < 0 or target_alt > 90):
		#print("c to cancel, ? to get status.")
		#key = getkey()
		#if key == '?': get_location()
		#elif key == 'c': break
	
		print ("Will move Az from " + str(azimuth) + " to " + str(target_az) + " and Alt from " + str(altitude) + " to " + str(target_alt))
		
		delta_az = abs(target_az - azimuth)
		delta_az %= 360.0
		delta_az = 180.0 - abs(delta_az - 180.0)
		if (azimuth + delta_az) % 360.0 == target_az:
			direction_az = "right"
		else: direction_az = "left"
		
		if altitude > 180: delta_alt = target_alt - altitude + 360
		else: delta_alt = target_alt - altitude
		direction_alt = ("down", "up")[delta_alt > 0.0]

		move(amount_az = delta_az, direction_az = direction_az, speed_az = SPEED_AZ,
			amount_alt = abs(delta_alt), direction_alt = direction_alt, speed_alt = SPEED_ALT)
		
		# accept keyboard input (c or tuning directions) while waiting between moves
		#sleep(track_refresh_interval)
		try:
			if wait_for( track_refresh_interval ) ==  True: break
		except KeyboardInterrupt as err: # accept Ctrl+c
			pass
		
		#print ("...next move now...")
		target_az, target_alt = search_0(location)





################## print info


def get_location():
	print("Curent Az: " + str(azimuth) + ", Alt: " + str(altitude))

def get_status():
	get_location()
	if same != "": print ("Last successfull searched body:" + same)
	
	print("Speed Az: " + str(SPEED_AZ) + ", Alt: " + str(SPEED_ALT))
	print ("Time to complete 0 to 360 deg rotation (Az): " +  str(360.0 / SPEED_AZ) + " seconds.")
	print ("delay (Az): " + str(delay_AZ) + " seconds.")
	
	print ("Time to complete 0 to 90 deg rotation (Alt): " +  str(90.0 / SPEED_ALT) + " seconds.")
	print ("delay (Alt): " + str(delay_ALT) + " seconds.")
	
	print("Microstepping Az: " + str(microstep_az) + ", Alt: " + str(microstep_alt))
	
	print("Track refresh interval: " + str(track_refresh_interval) + " seconds." )









################## main

def quit_nicely():
	GPIO.cleanup()

def show_options():
	print ("\nAvailable options:")
	print ("0. set location")
	print ("1. move to location")
	print ("2. track body")
	print ("3. get status")
	print ("4. set track refresh interval")
	print ("5. set microstepping")
	print ("6. set speed (deg/sec)")
	print ("7. get location")
	print ("8. manual drive")
	print ("9. fuck off")
	print ("10. recover last location")
	print ("11. set observer location")
	print ("12. get observer location")

def switch_main(option):
	switcher = {
		0: set_location,
		1: go_to_location,
		2: track,
		3: get_status,
		4: set_track_refresh_interval,
		5: set_microstepping,
		6: set_speed,
		7: get_location,
		8: manual_drive,
		9: quit_nicely,
		10: recover_last_location,
		11: set_observer,
		12: get_observer
	}
	func = switcher.get(option, show_options)
	func()

################

show_options()
option = int(input("what is my purpose?"))
while option != 9:
	switch_main(option)
	
	show_options()
	option = int(input("what is my purpose?"))


#GPIO.cleanup()
quit_nicely()

print ("good riddance!")


