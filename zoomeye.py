import sys
import os
import json
import requests
from Queue import Queue
import re

class Zoomeye(object):
    def __init__(self):
        self.API_URL = "http://www.zoomeye.org/api/query"
        self.API = None

    def getConfig(self):
        if os.path.exists("config.txt"):
            config = {}
            fp = open("config.txt", "r")
            for eachLine in fp:
                if "=" in eachLine:
                    eachConfig = eachLine.split("=")
                    config[eachConfig[0].strip()] = eachConfig[1].strip()
            self.API_TOKEN = config['API_TOKEN']
        else:
            print "you must config your API_TOKEN for the first time"
            sys.exit()

    def searchIP(self, query, pages, queue, STOP_ME):
        if self.API_TOKEN == None:
            print "please config your API_TOKEN"
            sys.exit()
        for page in range(1, pages+1):
            try:
                header = {"Authorization": self.API_TOKEN}
                res = requests.get("%s?keyword=%s&type=host&page=%s" % (self.API_URL, query, page), headers = header)
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
                        result_iter = iter(results["results"])
                        for result in result_iter:
                            if re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", result["ip"]):
                                queue.put(result["ip"])
        STOP_ME[0] = True