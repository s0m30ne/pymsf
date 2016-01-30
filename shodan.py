import sys
import os
import json
import requests
import time
import math
from Queue import Queue

class Censys(object):
    def __init__(self):
        self.API_URL = "https://www.censys.io/api/v1"
        self.UID = None
        self.SECRET = None

    def getConfig(self):
        if os.path.exists("config.txt"):
            config = {}
            fp = open("config.txt", "r")
            for eachLine in fp:
                if "=" in eachLine:
                    eachConfig = eachLine.split("=")
                    config[eachConfig[0].strip()] = eachConfig[1].strip()
            self.UID = config['UID']
            self.SECRET = config['SECRET']
        else:
            print "you must config your UID and SECRET for the first time"
            sys.exit()

    def searchIP(self, query, pages, queue, STOP_ME):
        if self.UID == None or self.SECRET == None:
            print "please config your UID and SECRET"
            sys.exit()
        for page in range(1, pages+1):
            start_time = time.time()
            data = {
                "query":query, 
                "page":page, 
                "fields":["ip", "autonomous_system.name"]
            }
            try:
                res = requests.post(self.API_URL + "/search/ipv4", data=json.dumps(data), auth=(self.UID, self.SECRET))
            except:
                print "request error"
                continue
            else:
                try:
                    results = res.json
                except:
                    print "json decode error !"
                    continue
                else:
                    if res.status_code != 200:
                        print "error occurred: %s" % results["error"]
                        sys.exit(1)
                    else:
                        result_iter = iter(results["results"])
                        for result in result_iter:
                            queue.put(result["ip"])
            end_time = time.time()
            used_time = end_time - start_time
            if used_time > 2.5:
                pass
            else:
                time.sleep(math.ceil(used_time))
        
        STOP_ME[0] = True
