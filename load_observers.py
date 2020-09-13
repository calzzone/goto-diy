
##### observers (observing location on the earth)
# ephem knows a list of cities, but it's too small.
# TODO: use some online thing to get gps coordinates, elevation and even pressure and temperature

#import string
import ephem
#from ephem import *

# Reads observers_file and returns a dictionary of observer_names : ephem.Observer pairs
def gather_observers(observers_file):

	observers_lines = open(observers_file, "r").readlines()
	observers = {}

	for line in observers_lines:
		line = line.strip()

		# Skip comments
		if line.startswith('#'): continue # try next line
		pound = line.find("#")
		if pound >= 0: line = line[:pound] # remove comments at the end of the line

		# new observer
		elements = str(line).split(sep=';')
		if len(elements) < 3: continue # not a valid observer; try next line
		observer = ephem.Observer()
		observer.lat, observer.lon = elements[1], elements[2]

		if len(elements) >= 3:
			observer.elevation = float(elements[3])

		if len(elements) >= 4:
			observer.pressure, observer.temp = float(elements[4]), float(elements[5])
		else:
			observer.pressure, observer.temp = 1013, 15 # Stellarium settings

		observers[elements[0]] = observer

	return (observers)


# Sets an observer. If calld with a valid observer name, sets it; otherwise, asks for one.
# Can be called from the UI, with no argument.
# CRITICAL: first time has to be successfull.
# On failure subsequent times, does not change the previously set observer.

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

# Print info about the global observer (if no args provied) or a specified observer
def print_observer(_observer_name = None, _observer=None):
	if _observer_name == None: _observer_name = observer_name
	if _observer == None: _observer = observer

	print ( "Current observing location: " + _observer_name + ":")
	print ( "Lat: " + str(_observer.lat) + " Lon: " + str(_observer.lon) +
			" Elevation: " + str(_observer.elevation) + "\n" +
			"Pressure: " + str(_observer.pressure) + " Temp: " + str(+observer.temp) )

# observers_file = "observers.txt"
# observer_name = "cluj" # default observer; has to be present in observers_file
# observers = gather_observers(observers_file)
# observer, observer_name = set_observer(observer_name)
