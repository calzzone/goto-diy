
# global variables
import config
from config import *

#from print_functions import * # soon to be implemented...
from backup_location import *
from move_function import *
from ephem_wrapper import *

# let the user specify a location (coordinates or named body) and go there
def go_to_location():
	target_az =  -1
	target_alt = -1
	while target_az < 0 or target_az >= 360 or target_alt < 0 or target_alt > 90:
		#target_az, target_alt = map(float, input("Target Az [0-360) Alt [0-90 deg]: (-360 to cancel) ").split())
		target_az, target_alt = search()
		if (target_alt == None or target_az == None):
			return()
		if (target_alt == config.altitude and target_az == config.azimuth):
			return()

	if config.azimuth != target_az:
		print ("Will should Az from " + str(config.azimuth) + " to " + str(target_az))
	if config.altitude != target_alt:
		print ("Will should Alt from " + str(config.altitude) + " to " + str(target_alt))


	Az = config.azimuth + 360.0
	TAz = target_az + 360.0
	delta_az_right = (TAz - Az) % 360.0
	delta_az_left  = (Az - TAz) % 360.0

	delta_az = min(delta_az_right, delta_az_left)
	direction_az = ("left", "right")[delta_az_right < delta_az_left]

	if config.altitude > 180: delta_alt = target_alt - config.altitude + 360 # TODO: should not happen under regular usage!
	else: delta_alt = target_alt - config.altitude
	direction_alt = ("down", "up")[delta_alt > 0.0]

	move(amount_az = delta_az, direction_az = direction_az, speed_az = config.speed_Az,
		amount_alt = abs(delta_alt), direction_alt = direction_alt, speed_alt = config.speed_Alt)
