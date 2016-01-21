import sys
import os
import json
import requests
from Queue import Queue
import re

class Shodan(object):
    def __init__(self):
        self.API_URL = "https://api.shodan.io/shodan/host/search"
        self.API_KEY = None

    def getConfig(self):
        if os.path.exists("config.txt"):
            config = {}
            fp = open("config.txt", "r")
            for eachLine in fp:
                if "=" in eachLine:
                    eachConfig = eachLine.split("=")
                    config[eachConfig[0].strip()] = eachConfig[1].strip()
            self.API_KEY = config['API_KEY']
        else:
            print "you must config your API_KEY for the first time"
            sys.exit()

    def searchIP(self, query, pages, queue, STOP_ME):
        if self.API_KEY == None:
            print "please config your API_KEY"
            sys.exit()
        for page in range(1, pages+1):
            try:
                res = requests.get("%s?key=%s&query=%s&page=%s" % (self.API_URL, self.API_KEY, query, page))
            except:
                print "request error"
                continue
            else:
                try:
                    results = res.json
                    if not isinstance(results, dict):
                        results = res.json()
                except:
                    print "json decode error !"
                    continue
                else:
                    if results.has_key("error"):
                        print "error occurred: %s" % results["error"]
                        sys.exit(1)
                    else:
                        result_iter = iter(results["matches"])
                        for result in result_iter:
                            if re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", result["ip_str"]):
                                queue.put(result["ip_str"])
        STOP_ME[0] = True