
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

###### available named bodies

# named stars built into ephem # TODO: remove this, maybe
list_of_ephem_stars = open("ephem_stars.txt", "r").readlines()
list_of_ephem_stars = [star[:-1].lower() for star in list_of_ephem_stars]

# named stars from YBS
list_of_named_stars = open("named_stars.txt", "r").readlines()
list_of_named_stars = [star[:-1].lower() for star in list_of_named_stars]

# named stars in an other catalog
list_of_stars_YBS = open("YBS2.txt", "r").readlines()
list_of_stars_YBS = [star[:-1].lower() for star in list_of_stars_YBS]


# TODO: add some interactivity
def print_named_stars():
	print("List of available named stars:")
	print(", ".join(list_of_named_stars))

# TODO: A lot of them: have some way of printing in chunks
def print_available_stars():
	print("List of all available stars:")
	print(", ".join(list_of_stars_YBS))




# TODO: Currently not really used. Just a SackOverflow relic.
# There is a way to infer what kind of celestial body is one
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
		# ? is not formally implemented; just a quick way to deal with missing values.

	if subfields[0] == 'f':
		return FIXED_BODY_MAP[subfields[1]]

	return "?"

# Reads an arbitrary edb file.
# Returns a list of bodies, each a tubple with: name, description, the ephem representation of the body
def read_database( filename ):
	# Read a set of bodies from an EDB file.
	bodies = []
	#desc = {}

	# Read the file.
	with open(filename) as f:
		# Look at each line of the file
		for line in f:
			line=line.strip()

			# Skip comments
			if line.startswith('#'): continue

			# Skip malformed lines
			if "," not in line:	continue

			# describe body
			#line = line.replace(",f,", ",f|?,") # temporary precausion to make describe_body() shut up; most are already done

			elements = line.split(",") # Split the line apart.
			name = elements[0] # Extract the name
			subfields = elements[1].split('|') # Extract the type fields
			desc = describe_body(subfields) # Map those to a description

			# Give the whole line to pyephem; # revent the previous "fix"
			body = ephem.readdb(line.replace(",f|?,", ",f,"))

			bodies.append( (name, desc, body) )

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


# make a fake star, mostly for tracking arbitrary Az/Alt
fake_star = ephem.FixedBody()
def make_fake_star(az = None, alt = None):
	if az is None or alt is None: # no args
		az, alt = input("Define fake star by Az Alt: ").strip().split().map(float)

	global fake_star
	fake_star = ephem.FixedBody()
	fake_star._ra, fake_star._dec = observer.radec_of(az, alt)
	fake_star._epoch = ephem.J2000
	#fake_star.compute( observer )
	#print( cano.az, cano.alt)
	return fake_star

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
	elif target.lower() in list_of_ephem_stars:
		thing = ephem.star(string.capwords(target))
	elif target.lower().strip() in list_of_stars_YBS:
		YBS2 = read_database("YBS2.edb")
		star = list_of_stars_YBS.index( target.lower().strip() )
		print("Other stars catalog: " + YBS2[star][0])
		thing = YBS2[star][2]
	elif target == "fake": # fake body, defined by az/alt
		thing = fake_star
	elif target[0] == '#' and target[1:].isnumeric() : # landmarks, defined by az/alt
        #landmarks = gather_landmarks(landmarks_file)
		landmark = int(target[1:].strip())-1
		return( landmarks[landmark]["Az"], landmarks[landmark]["Alt"] )
	else: return(None)

	if thing is None: return (None)

	return(compute(thing, observer))

# actual search function called from the UI
def search():
	global same # TODO: the error!
	global same_str

	while True:
		same_str_builder = ": " + same_str if same_str != "" else ""
		print("Search for celestial body. To list stars in YBS catalogue type 'named' or 'all'. To list landmakrs type 'landmarks'.")
		location = input("Location (`home`, Az [0-360) Alt [0-90 deg], common name, 'same`" + same_str_builder + " or 'c' to cancel): ")
		if location == "named":
			print_named_stars()
			continue
		if location == "all":
			print_available_stars()
			continue
		if location == "landmakrs":
			print_landmarks()
			continue

		if location == "same": location = same
		elif location == "home": location = "0 0"
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
