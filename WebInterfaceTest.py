#!/bin/python3

# Imports
import http.server
import random
import requests
import queue
import threading
import time
from collections import deque
import json
import os

# Functions
def runServer(ip='', port=8080):
    global httpd, webInterfaceAuth, keepWebIntAlive, LastRequestForWebInt
    webInterfaceAuth = keepWebIntAlive = LastRequestForWebInt = None
    httpd = http.server.ThreadingHTTPServer((ip, port), WebInterfaceServer)
    asyncTimeoutFunc(120, webInterfaceTimeout) #Starting timeout of 120 seconds
    httpd.serve_forever()

def encDec(key, val):
    res = ''
    i = 0
    while i<len(val):
        res += chr(ord(key[i % len(key)])^ord(val[i]))
        i += 1
    return res
def funcWithDelay(delay, func, args=[], kwargs={}):
    time.sleep(delay)
    func(*args, **kwargs)
def asyncTimeoutFunc(delay, func, args=[], kwargs={}):
    threading.Thread(target=funcWithDelay, args=[delay, func]+args, kwargs=kwargs, daemon=True).start()
def webInterfaceTimeout(*args):
    print (args)
    #global keepWebIntAlive
    #while True: #Checks every 40 seconds after running if "keepWebIntAlive" is true, if it isn't then it will close the server.
    #    if not keepWebIntAlive: break
    #    if httpd:
    #        pass
    #    keepWebIntAlive = False
    #    time.sleep(40)
    webInterfaceAuth = None
    web_data.clear()
    print ('Web interface timed out - Stopping...')
    httpd.shutdown()
    httpd.socket.close()

# Classes
class WebInterfaceServer(http.server.BaseHTTPRequestHandler):
    def do_GET(self): #Overwrite what happens when the client sends a GET request
        global webInterfaceAuth, LastRequestForWebInt, keepWebIntAlive
        if LastRequestForWebInt == None: LastRequestForWebInt = time.time()
        elif time.time() < LastRequestForWebInt+0.1: #Rate limiting
            self.send_response(429) #Response: 429 Too Many Requests
            self.end_headers()
            LastRequestForWebInt = time.time()
            return
        LastRequestForWebInt = time.time()
        keepWebIntAlive = True #Keep the server alive every time a GET request is recieved
        if (webInterfaceAuth != None) and (webInterfaceAuth[1] != self.client_address[0]):
            self.send_response(409) #Response: 409 Conflict
            self.end_headers()
            self.wfile.write('Error 409: Conflict\nThis interface is currently reserved for another IP address. Please try again later')
            return
        if self.path == '/': #Root/main directory, send HTML
            self.send_response(200) #Response: 200 OK
            self.send_header('Content-type', 'text/html') #HTML text
            self.end_headers()
            self.wfile.write(b'<script>window.onload=function(){fetch(\'https://raw.githubusercontent.com/Tiger-Tom/RunServerDotPy-extras/main/WebServer/WebServer.html\').then(r=>r.text()).then(function(d){document.open(\'text/html\', \'replace\').write(d)})}</script>') #Fetch and write HTML text
        else: #Otherwise, use match..case
            match self.path.removeprefix('/').split('/'): #Match with the path, split by /, with the first / removed as it is unneeded
                case ['_data']:
                    if webInterfaceAuth != None:
                        self.send_response(200) #Response: 200 OK
                        self.send_header('Content-type', 'text/plain')
                        self.end_headers()
                        self.wfile.write(bytes(encDec(webInterfaceAuth[0], str(list(web_data))), 'UTF-8'))
                        web_data.clear()
                    else: #If it is not authenticated
                        self.send_response(401) #Response: 401 Unauthorized
                        self.end_headers()
                case ['_auth', 'init']: #Initialize authentication
                    if webInterfaceAuth == None:
                        webInterfaceAuth = (('%030x' % random.randrange(16**30)), self.client_address[0]) #Generate 30 random hexadecimal bits as password
                        print ('Password: "'+webInterfaceAuth[0]+'" (IP: '+webInterfaceAuth[1]+')')
                        self.send_response(200) #Response: 200 OK
                        self.end_headers()
                    else:
                        self.send_response(409) #Response: 409 Conflict
                        self.end_headers()
                case ['_auth', 'test']: #Test authentication
                    if webInterfaceAuth != None:
                        self.send_response(200) #Response: 200 OK
                        self.send_header('Content-type', 'text/plain')
                        self.end_headers()
                        self.wfile.write(bytes(encDec(webInterfaceAuth[0][::-1], webInterfaceAuth[0]), 'UTF-8'))
                    else: #If it is not authenticated
                        self.send_response(401) #Response: 401 Unauthorized
                        self.end_headers()
                case _: #Path is unknown, send 404 File not Found
                    self.send_response(404) #Response: 404 Not found
                    self.end_headers()
    def do_POST(self):
        global webInterfaceAuth, LastRequestForWebInt, keepWebIntAlive
        if LastRequestForWebInt == None: LastRequestForWebInt = time.time()
        elif time.time() < LastRequestForWebInt+0.01: #Rate limiting
            self.send_response(429) #Response: 429 Too Many Requests
            self.end_headers()
            LastRequestForWebInt = time.time()
            return
        if int(self.headers['Content-Length']) > 500: #If the data/content/"Payload" is too big (more than 500 chars)
            self.send_response(413) #Response: 413 Payload Too Large
            self.end_headers()
            return
        data = self.rfile.read(int(self.headers['Content-Length'])).decode('UTF-8')
        print (data)
        if self.path == '/_send/cmd':
            data = encDec(webInterfaceAuth[0], data)
            print (data)
            if data:
                if not data.startswith(chatComPrefix): data = chatComPrefix+data
                if data.startswith(chatComPrefix+'root'): self.send_response(403) #Response: 403 Forbidden
                else:
                    self.send_response(200) #Response: 200 OK
                    inputQueue.append(data)
                self.end_headers()
            else: self.send_response(400) #Response: 400 Bad Request
            self.end_headers()
        elif self.path == '/_send/end':
            if (webInterfaceAuth != None) and (encDec(webInterfaceAuth[0], data) == 'end'):
                webInterfaceAuth = None
                self.send_response(200) #Response: 200 OK
                self.end_headers()
                self.server.shutdown()
                self.server.socket.close()
                web_data.clear()
            else:
                self.send_response(401) #Response: 401 Unauthorized
                self.end_headers()
        else:
            self.send_response(404) #Response: 404 Not Found
            self.end_headers()
    def log_message(self, format, *args): return #Silence logging messages
#class WebInterfaceTCP(socketserver.BaseRequestHandler):
#    def handle(self):
#        self.data = self.request.recv(1024).strip()
#        print (self.data)
#        self.request.sendall(('{} {} HTTP/1.1\nhost: localhost'.format('POST', 'text/plain')).encode('UTF-8'))

#1017
#logData(, 'WebInterface')
#webInterfaceAuthUser

# Testing/temp variables
chatComPrefix = ';'
cacheDir = './RunServerDotPy/Cache/' # ./RunServerDotPy/Cache/
def loadHelp():
    global chatCommandsHelp,chatCommandsHelpAdmin,chatCommandsHelpRoot
    with open(cacheDir+'ChatCommandsHelp.json') as f:
        chatCommandsHelp,chatCommandsHelpAdmin,chatCommandsHelpRoot = json.load(f) #Load ChatCommands help from cached JSON file

def writeCommand(comm):
    inputQueue.append('/'+comm)
loadHelp()

# Main
threading.Thread(target=runServer, daemon=True).start()
num = 0
web_data = deque(maxlen=20)
inputQueue = deque()
keepWebIntAlive = None
while True:
    #web_data.append(str(num))
    web_data.append(str(num))
    if inputQueue: web_data.append(inputQueue.popleft())
    num += 1
    time.sleep(1)
