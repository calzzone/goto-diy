
import json

with open('settings.json') as config_file:
    settings = json.load(config_file)

width = settings['width']
#height = settings['height']

