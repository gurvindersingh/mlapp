import json

CONFIG = {}

with open('config.json', 'r') as conffile:
    CONFIG = json.load(conffile)