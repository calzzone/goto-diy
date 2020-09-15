# global variables
import config
from config import *

# Landmarks: the same format as observers
# TODO: add more flexibility; maybe a folder with landmakrs, posibility to choose at runtime, correlate to observer locations

# reads landmarks_file and returns a list of dictionaries (each is a landmarks wih name, Az, Alt)
def gather_landmarks(_landmarks_file):

	landmarks_lines = open(_landmarks_file, "r").readlines()
	landmarks = []

	for line in landmarks_lines:
		line = line.strip()

		# Skip comments
		if line.startswith('#'): continue # try next line
		pound = line.find("#")
		if pound >= 0: line = line[:pound] # remove comments at the end of the line

		# new landmark
		elements = str(line).split(sep=';')
		if len(elements) != 3: continue # not a valid observer; try next line

		landmark = { "name": elements[0], "Az": float(elements[1]), "Alt": float(elements[2]) }

		landmarks.append( landmark )

	return (landmarks)


# Print global landmarks
def print_landmarks():
	print ("Current landmarks file: " + TColors.orange_on_black + config.landmarks_file + TColors.normal + ":")

	i = 0
	for landmark in config.landmarks:
		print(str(i+1) + ": " +
			TColors.orange_on_black + landmark["name"] + TColors.normal +
			": Az=" + TColors.blue_on_black + str(landmark["Az"]) + TColors.normal +
			": Alt=" + TColors.blue_on_black + str(landmark["Alt"]) + TColors.normal)
		i += 1

#####

#config.landmarks_file = "balcon_sud.landmakrs"
#config.landmarks = gather_landmarks(config.landmarks_file) # in main
