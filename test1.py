from time import sleep
from datetime import datetime

import string

import ephem
from ephem import *	  

observers_file = "observers.txt"

# reads observers_file and returns a dictionary of observer_names : ephem.Observer pairs
def gather_observers():
	
	observers_lines = open(observers_file, "r").readlines()
	observers = {}
	
	
	for line in observers_lines:
		line = line.strip()
	
		# Skip comments
		if line.startswith('#'):
			continue
		
		pound = line.find("#")
		if pound >= 0:
			line = line[:pound]
		
		# new observer #TODO: does not work!!!
		elements = str(line).split(sep=';') 
		if len(elements) < 3: continue
		
		observer = ephem.Observer()
		observer.lat, observer.lon = elements[1], elements[2]
		
		if len(elements) >= 3:
			observer.elevation = float(elements[3])
		
		if len(elements) >= 4:
			observer.pressure, observer.temp = float(elements[4]), float(elements[5])
		else: 
			observer.pressure, observer.temp = 1013, 15# stellarium settings
		
		observers[elements[0]] = observer
	
	return (observers)

observers = gather_observers()

def set_observer(new_observer = None):
	with_arg = True if new_observer is None else False
	while True:
		if with_arg: # if new_observer is None:
			print ("Currently available obsever locations as defined in " + observers_file + ": " + ", ".join(observers.keys()) + ". ")
			new_observer = input("Type the name of the observer location or 'c' to cancel: ")
		
		if new_observer == "c": return ()
		elif new_observer in observers.keys():
			#observer = observers
			if with_arg:
				global observer
				global observer_name
				observer, observer_name = observers[new_observer], new_observer
			return (observers[new_observer], new_observer)


#observer = ephem.Observer() # have a default
observer_name = "cluj"
observer, observer_name = set_observer(observer_name)

print("Observer is: ")
print (observer)

set_observer()

print("Observer is: ")
print(observer)
