import json

comp = {}

with open("comp.json", "r") as comp_file:
    try:
        comp = json.loads(comp_file.read())
    except json.JSONDecodeError:
        pass # No data

def save():
    with open("comp.json", "w") as comp_file:
        comp_file.write(json.dumps(comp))