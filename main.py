
from load_settings import *

# import json
# with open('settings.json') as config_file:
#     settings = json.load(config_file)
# width = settings['width']
#height = settings['height']

# print(width)
# print(settings['height'])

#a = 3

def function1_inside_main():
    global a
    a = a+1

function1_inside_main()
print(a)

#x = input("x=")
