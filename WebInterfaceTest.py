#!/bin/python3

# Imports
import http.server
import random
import requests
import queue
import threading
import time
#import  ## NEEDS PIP INSTALL ([pyBin] -m pip install )!!!!!!!!! #####################

# Functions

def getFileFromServer(url, encoding=None):
    print ('GET >'+url+'< [encoding='+str(encoding)+']')
    r = requests.get(url)
    if encoding != None: r.encoding = encoding
    r.close()
    return r.text


def runServer(ip='', port=8080):
    httpd = http.server.ThreadingHTTPServer((ip, port), WebInterfaceServer)
    httpd.serve_forever()

# Classes
def encDec(key, val):
    res = ''
    i = 0
    while i<len(val):
        res += chr(ord(key[i % len(key)])^ord(val[i]))
        i += 1
    return res
authPass = None
class WebInterfaceServer(http.server.BaseHTTPRequestHandler):
    def do_GET(self): #Overwrite what happens when the client sends a GET request
        global authPass
        if self.path == '/': #Root/main directory, send HTML
            self.send_response(200) #Response: 200 OK
            self.send_header('Content-type', 'text/html') #HTML text
            self.end_headers()
            #self.wfile.write(b'<script>window.onload=function(){fetch(\'https://raw.githubusercontent.com/Tiger-Tom/RunServerDotPy-extras/main/WebServer/WebServer.html\').then(r=>r.text()).then(function(d){document.open(\'text/html\', \'replace\').write(d)})}</script>') #Send HTML text
            self.wfile.write(b'''<!DOCTYPE html>
<html>
    <head>
        <title>RS.py WebInterface</title>
        <script>
        function handleErrors(response) { // Thanks, https://www.tjvantoll.com/2015/09/13/fetch-and-errors/ !
            window.res = response;
            if (!response.ok) {
                throw Error(JSON.stringify({'status': response.status, 'text': response.statusText, 'body': response.body}));
            }
            return response;
        }
        function mainLoop() {
            window.loopID = window.setInterval(function() {
                elemID = 'main';
                fetch('./_data').then(handleErrors).then(res => res.text()).then(function(data) {
                    try {
                        dataParsed = (JSON.parse(encDec(window.mainAuth, data).replaceAll('\\'', '"')).reverse().join('\\n'));
                        document.getElementById(elemID).innerHTML = dataParsed+'\\n'+document.getElementById(elemID).innerHTML;
                    } catch (e) {}
                }).catch(function (e) {
                    console.log(e);
                    if (e.status == 401) {
                        alert('401 "Unauthorized" recieved. Maybe the session expired, or was never created in the first place?');
                    } else {
                        alert(e.status+' "'+e.text+'" recieved, this error is unexpected and may be a sign of instability');
                    }
                });
                height = Math.round(window.innerHeight/15)-100;
                if (document.getElementById(elemID).innerHTML.split('\\n').length > height) {
                    document.getElementById(elemID).innerHTML = document.getElementById(elemID).innerHTML.split('\\n').slice(0, height).join('\\n');
                }
            }, 5000);
        }
        function setupAuth() {
            fetch('./_auth/init').then(handleErrors).then(res => res.text()).then(function(data) {
                document.getElementById('reauthDiv').style.display = 'none';
                document.getElementById('auth_input').type = 'password';
                document.getElementById('click_auth').onclick = testAuth;
                document.getElementById('click_auth').innerHTML = 'Test Passcode';
            }).catch(function(e) {
                if (e.status == 409) {
                    alert('409 "Conflict" recieved. Perhaps the server has been authenticated with another user?');
                } else {
                    alert(e.status+' "'+e.text+'" recieved, this error is unexpected and may be a sign of instability');
                }
            });
        }
        function testAuth() {
            fetch('./_auth/test').then(handleErrors).then(res => res.text()).then(function(data) {
                console.log(data);
                console.log(encDec(document.getElementById('auth_input').value.split('').reverse().join(''), data));
                if (encDec(document.getElementById('auth_input').value.split('').reverse().join(''), data) == document.getElementById('auth_input').value) {
                    document.getElementById('authDiv').style.display = 'none';
                    document.getElementById('mainDiv').style.display = 'block';
                    document.getElementById('main').style.height = (window.innerHeight-100)+'px';
                    window.mainAuth = document.getElementById('auth_input').value;
                    alert('Authenticated');
                    mainLoop();
                } else {
                    alert('Authentication failure');
                }
            }).catch(function(e) {
                if (e.status == 401) {
                    alert('401 "Unauthorized" recieved. Maybe the session expired, or was never created in the first place?');
                } else {
                    alert(e.status+' "'+e.text+'" recieved, this error is unexpected and may be a sign of instability');
                }
            });
        }
        function encDec(key, val) {
            res = '';
            for (i=0; i<val.length; i++) {
                res += String.fromCharCode(key.charCodeAt(i % key.length)^val.charCodeAt(i));
            }
            return res;
        }
        function killServer() {
            window.clearInterval(window.loopID);
            navigator.sendBeacon('./_send/end', encDec(window.mainAuth.split('').reverse().join(''), window.mainAuth()));
            if (confirm('Close window?')) {
                window.close();
            } else {
                document.getElementById('authDiv').style.display = 'block';
                document.getElementById('mainDiv').style.display = 'none';
                document.getElementById('auth_input').type = 'hidden';
                document.getElementById('click_auth').onclick = setupAuth;
                document.getElementById('click_auth').innerHTML = 'Initialize Authentication';
                document.getElementById('reauthDiv').style.display = 'block';
            }
        }
        function reauth() {
            document.getElementById('auth_input').type = 'password';
            document.getElementById('click_auth').onclick = testAuth;
            document.getElementById('click_auth').innerHTML = 'Test Passcode';
            document.getElementById('reauthDiv').style.display = 'none';
        }
        function sendCommand() {}
        </script>
    </head>
    <body>
        <div id='authDiv'>
        <button id='click_auth' onclick='setupAuth()'>Initialize Authentication</button>
        <input type='hidden' id='auth_input' label='Input Passcode'></input>
        <div id='reauthDiv'>
        <button onclick='reauth()'>Bypass Initialization (Authenticate with Existing Password)</button>
        </div></div>
        <div id='mainDiv' style='display: none; font-size: 15px'>
        <label for='commInsert'>Enter command > </label>
        <input type='text' id='commInsert'></input><br>
        <button onclick='sendCommand()'>Send Command</button><br>
        <button onclick='killServer()'>End the web interface server</button><br>
        <textarea id='main' style='font-size: 15px'>TextArea</textarea>
        </div>
    </body>
</html>''')
        else: #Otherwise, use match..case
            match self.path.removeprefix('/').split('/'): #Match with the path, split by /, with the first / removed as it is unneeded
                case ['_data']:
                    if authPass != None:
                        self.send_response(200)
                        self.send_header('Content-type', 'text/plain')
                        self.end_headers()
                        self.wfile.write(bytes(encDec(authPass, str(web_data)), 'UTF-8'))
                        print (bytes(encDec(authPass, str(web_data)), 'UTF-8'))
                        web_data[:] = []
                    else: #If it is not authenticated
                        self.send_response(401) #Response: 401 Unauthorized
                        self.end_headers()
                case ['_auth', 'init']: #Initialize authentication
                    print (authPass)
                    if authPass == None:
                        authPass = ('%030x' % random.randrange(16**30)) #Generate 30 random hexadecimal bits as password
                        print ('Password: "'+authPass+'"')
                        self.send_response(200) #Response: 200 OK
                        self.end_headers()
                    else:
                        self.send_response(409) #Response: 409 Conflict
                        self.end_headers()
                case ['_auth', 'test']: #Test authentication
                    if authPass != None:
                        self.send_response(200) #Response: 200 OK
                        self.send_header('Content-type', 'text/plain')
                        self.end_headers()
                        self.wfile.write(bytes(encDec(authPass[::-1], authPass), 'UTF-8'))
                        print (encDec(authPass[::-1], authPass), 'UTF-8')
                    else: #If it is not authenticated
                        self.send_response(401) #Response: 401 Unauthorized
                        self.end_headers()
                case _: #Path is unknown, send 404 File not Found
                    self.send_response(404) #Response: 404 Not found
                    self.end_headers()
    def do_POST(self):
        global authPass
        data = self.rfile.read(int(self.headers['Content-Length'])).decode('UTF-8')
        if self.path == '/_send/comm':
            self.headers
            data
        elif self.path == '/_send/end':
            if (authPass != None) and (encDec(authPass[::-1], data) == authPass):
                authPass = None
                self.send_response(200) #OK
                self.end_headers()
            else:
                self.send_response(401) #Unauthorized
                self.end_headers()
    def log_message(self, format, *args): return #Silence logging messages
#class WebInterfaceTCP(socketserver.BaseRequestHandler):
#    def handle(self):
#        self.data = self.request.recv(1024).strip()
#        print (self.data)
#        self.request.sendall(('{} {} HTTP/1.1\nhost: localhost'.format('POST', 'text/plain')).encode('UTF-8'))
        

# Main
threading.Thread(target=runServer, daemon=True).start()
num = 0
web_data = []
while True:
    web_data.append(str(num))
    num += 1
    time.sleep(0.25)
