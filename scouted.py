import json

scouted = {}

with open("scouted.json", "r") as scouted_file:
    try:
        scouted = json.loads(scouted_file.read())
    except json.JSONDecodeError:
        pass # No data

def save():
    with open("scouted.json", "w") as scouted_file:
        scouted_file.write(json.dumps(scouted))