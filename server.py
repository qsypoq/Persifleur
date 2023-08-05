#!/usr/bin/python

import os
from multiprocessing import Process
import socketserver
import re
import http.server

web_dir = os.path.join(os.path.dirname(__file__), 'html')
os.chdir(web_dir)

os.system('cd /usr/src/app && python convert.py')

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if None != re.search('/api/cicd_debug', self.path):
            os.system('git -C /usr/src/app/sources pull')
            os.system('cd /usr/src/app && python convert.py')
            return
        else:
            http.server.SimpleHTTPRequestHandler.do_GET(self)

def serve_forever(server):
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

def multiprocessHTTP(address, process):
    server = socketserver.TCPServer(address, CustomHandler)

    for i in range(process):
        Process(target=serve_forever, args=(server,)).start()
        print(f"Process number {i + 1} started")
    serve_forever(server)

if __name__ == '__main__':
    server_address = ('0.0.0.0', 1337)
    multiprocessHTTP(server_address, 2)