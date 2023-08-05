#!/usr/bin/python

import os
from multiprocessing import Process
import socketserver
import re
import http.server

web_dir = os.path.join(os.path.dirname(__file__), 'html')
os.chdir(web_dir)

PORT = 1337

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if None != re.search('/api/cicd_debug', self.path):
            os.system('cd /usr/src/app && python convert.py')
            return
        else:
            http.server.SimpleHTTPRequestHandler.do_GET(self)

httpd = socketserver.ThreadingTCPServer(('', PORT),CustomHandler)

print("serving at port", PORT)
httpd.serve_forever()