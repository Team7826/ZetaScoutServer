import json

fields = {}

with open("fields.json", "r") as fields_file:
    try:
        fields = json.loads(fields_file.read())
    except json.JSONDecodeError:
        pass # No data

def save():
    with open("fields.json", "w") as fields_file:
        fields_file.write(json.dumps(fields))