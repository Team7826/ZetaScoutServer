import requests
import config

class NoTBAKeyError(Exception):
    pass

class TBAKeyInvalidError(Exception):
    pass

def get_has_key():
    return config.config["thebluealliance"].get("apikey", None) is not None

class TBA:

    def __init__(self):
        self.apikey = config.config["thebluealliance"].get("apikey", None)

        if not self.apikey:
            raise NoTBAKeyError("TBA key not found in config. Please add it before trying to initialize!")
        if not self.check_key_valid():
            raise TBAKeyInvalidError("Provided TBA key is not valid!")

    def get_events(self, season, query=None):

        resp = requests.get("https://www.thebluealliance.com/api/v3/events/" + season + "/simple", headers={
            "X-TBA-Auth-Key": self.apikey
        })
        data = resp.json()

        if query:
            for item in data:
                if query.lower() in item["name"].lower():
                    return item
        else:
            return data

    def get_matches(self, event_key):
        resp = requests.get(f"https://www.thebluealliance.com/api/v3/event/" + event_key + "/matches/simple", headers={
            "X-TBA-Auth-Key": self.apikey
        })
        return resp

    def check_key_valid(self):
        resp = requests.get(f"https://www.thebluealliance.com/api/v3/teams/1", headers={
            "X-TBA-Auth-Key": self.apikey
        })
        result = resp.json()
        if type(result) == list:
            return True
        return not "X-TBA-Auth-Key" in result.get("Error", "")