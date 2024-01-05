import json

config = {}

with open("config.json", "r") as config_file:
    config = json.loads(config_file.read())

def save():
    with open("config.json", "w") as config_file:
        config_file.write(json.dumps(config))