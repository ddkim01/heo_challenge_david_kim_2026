import requests

""" Most of code derived from https://www.space-track.org/documentation#/howto which shows example of "How to connect through the API using Python""""


class MyError(Exception):
    def __init__(self, args):
        Exception.__init__(
            self, "my exception was raised with arguments {0}".format(args)
        )
        self.args = args

# Sign into space-track.org with creds
username = "davidkim0168@gmail.com"
password = "INeedAWeapon117"

# Originally typed as one URL but split into parts for readability.
uriBase = "https://www.space-track.org"
requestLogin = "/ajaxauth/login"
requestCmdAction = "/basicspacedata/query"
requestFindIss = "/class/gp_history/NORAD_CAT_ID/25544/EPOCH/2025-01-01--2025-12-31/orderby/EPOCH%20asc/format/tle"
siteCred = {"identity": username, "password": password}

# POST for sending my creds to login, GET for requesting data 
with requests.Session() as session:
    resp = session.post(uriBase + requestLogin, data=siteCred)
    if resp.status_code != 200:
        raise MyError(resp, "POST fail on login")

    resp = session.get(uriBase + requestCmdAction + requestFindIss)
    if resp.status_code != 200:
        raise MyError(resp, "GET fail on request for ISS data")

# Claude's addition: Save the TLE data to a file for later use
    tle_data = resp.text
    print(f"Got {len(tle_data.strip().splitlines()) // 2} TLE sets")

    with open("iss_tle_2025.txt", "w") as f:
        f.write(tle_data)

