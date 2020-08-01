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



################## ephem

same = "0 0"
same_str = ""
same_coord = "Az 0 Alt 0"

list_of_stars = open("ephem_stars.txt", "r").readlines()
list_of_stars = [star[:-1].lower() for star in list_of_stars]
list_of_stars2 = open("YBS.txt", "r").readlines()
list_of_stars2 = [star[:-1].lower() for star in list_of_stars2]

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

			# Split the line apart.
			elements = line.split(",") 
			# Extract the name
			name = elements[0]
			# Extract the type fields
			subfields = elements[1].split('|') 
			# Map those to a description
			desc = describe_body(subfields)  
			
			# Give the whole line to pyephem
			body = readdb(line.replace(",f|?,", ",f,"))
			
			bodies.append( (name, desc,body) )
		
	return bodies

def dso_candidates(catalog_file):	
	# Read a catalog for DSO candidate targets.
	return read_database( catalog_file )

def compute(thing, observer):
	now = datetime.utcnow()
	observer.date = now
	#cluj.pressure = 0 
	#cluj.horizon="0:34"
	thing.compute(observer)
	print("Angle Az Alt:", thing.az, thing.alt)
	return(thing.az*180/math.pi, thing.alt*180/math.pi)
	#return(#ephem.degrees(thing.az), ephem.degrees(thing.alt), 
	#	thing.az*180/math.pi, thing.alt*180/math.pi)

cluj = ephem.Observer()
cluj.lat, cluj.lon = '46.7424895', '23.5650096'
cluj.elevation = 400
#cluj.date = '2020/7/17 12:52'

def find_body_by_name(name, catalog):
	for body in catalog:
		if body[0] == name:
			print(body)
			return body[2]
	return (None)

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
	elif target.lower()[0] == 'm' and int(target[1:]) <= 111: # TEMP: M111 = C/2020 F3 NEOWISE
		messier = dso_candidates("Messier.edb")
		name = "M" + target[1:].strip()
		thing = find_body_by_name(name, messier)
	elif target.lower().startswith('ic'): 
		ic = dso_candidates("IC.edb")
		name = "IC" + target[2:].strip()
		thing = find_body_by_name(name, ic)
	elif target.lower().startswith('ngc'): 
		ngc = dso_candidates("NGC.edb")
		name = "NGC" + target[3:].strip()
		thing = find_body_by_name(name, ngc)
	elif target.lower().startswith('ugc'): # also UGCA 
		ugc = dso_candidates("UGC.edb")
		name = "UGC" + target[3:].strip()
		thing = find_body_by_name(name, ugc)
	elif target.lower().endswith("xxx"): 
		neowise = dso_candidates("neowise.edb")
		name = target.upper().replace("XXX", "")
		thing = find_body_by_name(name, neowise)
	elif target.lower() in list_of_stars:
		thing = ephem.star(string.capwords(target))
	elif target.lower().strip() in list_of_stars2:
		YBS = dso_candidates("YBS.edb")
		star = list_of_stars2.index( target.lower().strip() )
		print("Other stars catalog: " + YBS[star][0])
		thing = YBS[star][2]
	else: return(None)

	if thing is None: return (None)
	
	return(compute(thing, cluj))


def search():
	global same
	global same_str
	
	print("List of available stars:")
	print(list_of_stars)
	
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
			if location[1] < 0: 
				alert = input("! Below horizon! Are you sure? [*/yes] ")
				if alert != "yes": 
					continue
			same_str = ""
			
		az, alt = location[0], location[1]
		print("Arbitrary location Az: " + str(az) + ", Alt: " + str(alt))
		
		same = temp
		return (az, alt)

##################


def show_options():
	print ("\nAvailable options:")
	print ("0. set location")
	print ("3. NA")

def set_location():
	global azimuth
	global altitude

	#azimuth, altitude = map(float, input("Current Az Alt: ").split()) 
	new_azimuth, new_altitude = search()
	if (new_azimuth == None or new_altitude == None):
		return()
	
	azimuth  = new_azimuth % 360.0	
	altitude = new_altitude  % 360.0

def switch_demo(option):
	switcher = {
		0: set_location,
		3: show_options
	}
	func = switcher.get(option, show_options)
	func()

################

show_options()
option = int(input("what is my purpose?"))
while option < 9:
	switch_demo(option)
	
	show_options()
	option = int(input("what is my purpose?"))


print ("good riddance!")



