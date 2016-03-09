import sys
import os
import json
import requests
import time
import math
from Queue import Queue

class Local(object):
    def __init__(self):
        pass

    def searchIP(self, queue, STOP_ME, startIP, endIP, ipfile):
        if ipfile:
            fp = open(ipfile, "r")
            for ip in fp:
                ip = ip.strip()
                queue.put(ip)
        else:
            ipstart = self.ip2num(startIP)
            ipend = self.ip2num(endIP)
            for targetip in range(ipstart, ipend + 1):
                strip = self.num2ip(targetip)
                queue.put(strip)
        
        STOP_ME[0] = True

    def ip2num(self, ip):
        ip = [int(x) for x in ip.split('.')]
        return ip[0]<<24 | ip[1]<<16 | ip[2]<<8 | ip[3]

    def num2ip(self, num):
        return '%s.%s.%s.%s' % ((num & 0xff000000) >> 24, (num & 0x00ff0000) >> 16, (num & 0x0000ff00) >> 8, num & 0x000000ff)
