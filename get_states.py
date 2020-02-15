'''
 Created on Fri Feb 14 2020:18:43:20
 Created by Ratnadeep Bhattacharya
'''

import requests
import json
import psutil
import time

URL = "http://192.168.1.134/status/format/json"

UPSTREAM_ZONES = ["compose_backend", "home_read_backend", "user_read_backend"]
NUM_SERVERS = 3
UPSTREAM_KEYS = ["requestCounter", "inBytes", "outBytes", "responses",
                 "requestMsecCounter", "weight", "maxFails", "failTimeout", "backup", "down"]

# STATES = []
STATE = {}


def get_json_status(url):
    """get the json for the current status"""
    status = requests.get(url).json()
    data = status["upstreamZones"]
    # print(status["serverZones"]["localhost"]["requestCounter"])
    for zone in UPSTREAM_ZONES:
        tmp = {}
        for srv in range(NUM_SERVERS):
            # print("SRV is: ", srv, " and zone is: ", zone)
            # print("Backend server: ", data[zone][srv]["server"])
            tmp[data[zone][srv]["server"]] = {}
            for k in data[zone][srv]:
                non_2xx_3xx_responses = 0
                if k in UPSTREAM_KEYS:
                    if k == "responses":
                        for k1 in data[zone][srv][k]:
                            if k1 in ["1xx", '4xx', '5xx']:
                                non_2xx_3xx_responses += data[zone][srv][k][k1]
                        # print("Non 2xx/3xx responses: ", non_2xx_3xx_responses)
                        tmp[data[zone][srv]["server"]
                            ]["Non 2xx/3xx responses"] = non_2xx_3xx_responses
                    elif k == "backup":
                        if data[zone][srv][k]:
                            # print("backup: ", 1)
                            tmp[data[zone][srv]["server"]]["backup"] = 1
                        else:
                            # print("backup: ", 0)
                            tmp[data[zone][srv]["server"]]["backup"] = 0
                    elif k == "down":
                        if data[zone][srv][k]:
                            # print("down: ", 1)
                            tmp[data[zone][srv]["server"]]["down"] = 1
                        else:
                            # print("down: ", 0)
                            tmp[data[zone][srv]["server"]]["down"] = 0
                    else:
                        # print(k, ": ", data[zone][srv][k])
                        tmp[data[zone][srv]["server"]][k] = data[zone][srv][k]
        STATE[zone] = tmp


def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName in proc.name():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def main(filename):
    up = checkIfProcessRunning("gen_load")

    with open(filename, 'w') as j:
        while (up):
            time.sleep(0.5)
            get_json_status(URL)
            up = checkIfProcessRunning("gen_load")
            json.dump(STATE, j)
            j.write("\n")


if __name__ == "__main__":
    import sys
    try:
        filename = sys.argv[1]
    except IndexError as e:
        sys.stderr.write("Missing Parameter\n")
        sys.exit(-1)
    main(filename)
