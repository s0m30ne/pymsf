import sys
import os
import json
import pycurl
import StringIO
from Queue import Queue

class Zoomeye(object):
    def __init__(self):
        self.API_URL = "http://api.zoomeye.org/host/search"

    def getConfig(self):
        if os.path.exists("config.txt"):
            config = {}
            fp = open("config.txt", "r")
            for eachLine in fp:
                if "=" in eachLine:
                    eachConfig = eachLine.split("=")
                    config[eachConfig[0].strip()] = eachConfig[1].strip()
            self.USERNAME = config['USERNAME']
            self.PASSWORD = config['PASSWORD']
            self.getToken()
        else:
            print "you must config your API_TOKEN for the first time"
            sys.exit()

    def getToken(self):
        user_auth = '{"username": "%s","password": "%s"}' % (self.USERNAME, self.PASSWORD)
        b = StringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL, "http://api.zoomeye.org/user/login")
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.CUSTOMREQUEST, "POST")
        c.setopt(pycurl.POSTFIELDS, user_auth)
        c.perform()
        ReturnData = json.loads(b.getvalue())
        self.API_TOKEN = ReturnData['access_token']
        b.close()
        c.close()

    def searchIP(self, query, pages, queue, STOP_ME):
        if self.API_TOKEN == None:
            print "please config your API_TOKEN"
            sys.exit()
        for page in range(1, pages+1):
            b = StringIO.StringIO()
            c = pycurl.Curl()
            c.setopt(pycurl.URL, "%s?query=%s&page=%s" % (self.API_URL, query, page))
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.CUSTOMREQUEST, "GET")
            c.setopt(pycurl.HTTPHEADER, ['Authorization: JWT %s' % self.API_TOKEN.encode()])
            c.perform()
            hosts = json.loads(b.getvalue())
            for host in hosts['matches']:
                queue.put(host["ip"])
        STOP_ME[0] = True
