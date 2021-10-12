#!/bin/python3

## This program is meant for Linux! Most things will probably work on Windows, but not everything. ##
## Macintoshes are also not supported ##

## This program must be run in unbuffered mode (default with "python3" command on Linux and Windows, but not IDLE) ##

# Imports

#  System
import os, sys, subprocess, platform
import gc, traceback
import threading

#  Numbers
import time
import math

#  Files
import shutil
import zipfile

#  Etc.
import random
import json
from collections import deque
from hashlib import md5

#  Non-builtin imports
try:
    import keyboard #For the keyboard "hook", to detect enter key presses
    import psutil #Will be used to close all trailing file handles, as well as getting some system informatino
    from better_profanity import profanity #For censoring and detecting profanity in chat
    import requests #For network/web requests to download files & data
except ModuleNotFoundError: #Means that we have to try to install the modules
    if input('Warning: some required modules were not found. Attempt to install? (Y/n) >').lower() == 'n': exit()
    modulesToInstall = 'keyboard psutil better_profanity pyspectator requests'
    print ('Installing...\n'+sys.executable+' -m pip install '+modulesToInstall)
    os.system('pip3 -q install '+modulesToInstall) #Install the modules (-q means quiet, to prevent a lot of spam in a console)
    del modulesToInstall # Free up memory, we will be seeing a lot of this
    #Try to import modules again
    import keyboard
    import psutil
    from better_profanity import profanity
    import requests

# Enforce minimum Python version
minVer = [3, 10] #[major, minor]
if (sys.version_info.major < minVer[0]) or ((sys.version_info.major == minVer[0]) and (sys.version_info.minor < minVer[1])):
    print ('This version is not supported!')

#  Check if speedtest-cli is installed, and install it if it isn't
if os.system('speedtest-cli --version'): #Return code is not 0
    if input('Speedtest is not installed ("speedtest-cli"). Attempt to install? (Y/n) >').lower() == 'n': exit()
    if os.name != 'nt': os.system('yes | apt-get install speedtest-cli') #Install for linux
    else: os.system('pip3 -q install speedtest-cli') #Fallback to install with PIP

# Directories
#All directories should be followed by a "/"
baseDir = os.path.split(os.getcwd())[0]+'/' # ../
srvrFolder = os.getcwd()+'/' # ./
confDir = srvrFolder+'RunServerDotPy/Config/' # ./RunServerDotPy/Config/
iconsDir = confDir+'Icons/' # ./RunServer/Config/Icons/
autoBckpZip = baseDir+'server-backup/main_backup.zip' # ../server-backup/main_backup.zip
logDir = srvrFolder+'RunServerDotPy/Logs/' # ./RunServerDotPy/Logs/
totalLogDir = logDir+'Total/' # ./RunServerDotPy/Logs/Total/
cacheDir = srvrFolder+'RunServerDotPy/Cache/' # ./RunServerDotPy/Cache/
modDir = srvrFolder+'RunServerDotPy/Mods/' # ./RunServerDotPy/Mods/

# Fix main RunServerDotPy directory if missing
if not os.path.exists(srvrFolder+'RunServerDotPy'): os.mkdir(srvrFolder+'RunServerDotPy')

# Setup some module-related things
gc.enable()

# Setup some values

#  "makeValues" values
sizeVals = ['bytes', 'kibibytes', 'mebibytes', 'gibibytes', 'tebibytes']
timeVals = ['seconds', 'minutes', 'hours']
longTimeVals = timeVals+['days', 'weeks']

#  Web interface values
webInterfaceAuth = keepWebIntAlive = lastRequestForWebInt = None

# Setup profanity filter
allowedProfaneWords = ['kill'] #Any words or phrases that should not be considered profane
allowedModifyWords = [] #Any words or phrases that may be a variation of a profane word, but should actually be allowed, as they are outputted in console
profanity.load_censor_words(whitelist_words=allowedProfaneWords) #whitelist_words - Whitelist some words ("kill" shows up in game, for instance, but is not a swear)
for i in allowedModifyWords:
    if i in profanity.CENSOR_WORDSET: del profanity.CENSOR_WORDSET[profanity.CENSOR_WORDSET.index(i)]

# Base simple functions

#  System commands
def runWOutput(cmd): #Runs a system command and returns the output
    out = subprocess.check_output(cmd, shell=True)
    if type(out) == bytes: return out.decode('UTF-8', 'replace') #Automatically decode it from UTF-8
    return out
def runWFullOutput(cmd, callbackFunc, callbackFuncXtraArgs=[]): #Runs a system command, and runns the callback function with each output
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    while True:
        out = proc.stdout.readline().decode('UTF-8', 'replace')
        if not len(out): break #If there is no output
        callbackFunc(out.lstrip().rstrip(), *callbackFuncXtraArgs)
def runWCallback(callbackFunc, cmd, onError=None): #Runs a system command and waits for it to finish, and then runs "callbackFunc" with the output as an argument
    try:
        callbackFunc(runWOutput(cmd))
    except:
        if onError != None: onError(callbackFunc, cmd)
def asyncRunWCallback(callbackFunc, cmd, onError=None): #Runs a system command with a callback, but asynchronously
    threading.Thread(target=runWCallback, args=(callbackFunc,cmd,onError), daemon=True).start()

#  Function functions
def funcWithDelay(delay, func, args=[], kwargs={}):
    time.sleep(delay)
    func(*args, **kwargs)
def asyncTimeoutFunc(delay, func, args=[], kwargs={}):
    threading.Thread(target=funcWithDelay, args=[delay, func]+args, kwargs=kwargs, daemon=True).start()

#  String formatting & similar
def makeValues(startValue, delimiter, values): #"values" is a list of strings (something like "second, minute, hour") in ascending order, "delimiter" is the divider (60 for "second, minute, hour"), and "startValue" is pretty obvious
    doneVals = {}
    previousVal = round(startValue)
    for i in range(len(values)):
        nextVal = math.floor(previousVal/delimiter)
        doneVals[values[i]] = previousVal-(nextVal*delimiter)
        previousVal = nextVal
    return doneVals
def makeValuesDiffDelimiter(startValue, delimiters, values): #"values" is a list of strings (something like "second, minute, hour", "day", "week") in ascending order, "delimiters" are the dividers ([60, 60, 24, 7] for "second, minute, hour, day, week"), and "startValue" is pretty obvious
    if len(delimiters) != len(values)-1: raise ValueError('Amount of delimiters is incorrect for amount of values (amount of delimiters should equal amount of values-1)')
    #doneVals = {values[0]: startValue}
    doneVals = {}
    delimiters.append(1)
    previousVal = round(startValue)
    for i in range(len(values)-1):
        nextVal = math.floor(previousVal/delimiters[i])
        doneVals[values[i]] = previousVal-(nextVal*delimiters[i])
        previousVal = nextVal
    #if previousVal != 0:
    doneVals[values[-1]] = previousVal
    return doneVals
def parseMadeValues(values, doReverse=True): #Removes values of 0, removes a trailing "s" if the corresponsing value is 1, adds commas and "and"s where appropriate, etc.
    newVals = {}
    for i in tuple(values):
        if values[i] != 0: #Corresponding value is not 0, so save it
            if i.endswith('s') and (values[i] == 1): newVals[i[:-1]] = str(values[i]) #Remove trailing "s" to make it singular instead of plural
            else: newVals[i] = str(values[i])
    if len(newVals) == 0: newVals = {tuple(values)[0]: str(tuple(values.values())[0])}
    if len(newVals) == 1: return tuple(newVals.values())[0]+' '+tuple(newVals)[0]
    elif len(newVals) == 2:
        indx = 0
        if doReverse: indx = 1
        return tuple(newVals.values())[indx]+' '+tuple(newVals)[indx]+' and '+tuple(newVals.values())[1-indx]+' '+tuple(newVals)[1-indx]
    else:
        print (newVals)
        res = ''
        keys = list(newVals)
        if doReverse: keys.reverse()
        for i in keys[:-1]:
            res += newVals[i]+' '+i+', '
        return res+'and '+newVals[keys[-1]]+' '+keys[-1]
def encDec(key, val): #Simple XOR bit encryption, used for web interface
    res = ''
    i = 0
    while i<len(val):
        res += chr(ord(key[i % len(key)])^ord(val[i]))
        i += 1
    return res

def pad0s(num, padAmount=1, padOn='left', autoRound=True): #Pads the number with the specified amount of zeroes (pad0s(1, 2) = 001 , pad0s(1, 2, 'right') = 100 (useful for decimals))
    if autoRound: num = int(num+0.5) #Thanks https://stackoverflow.com/questions/44920655/python-round-too-slow-faster-way-to-reduce-precision
    if num == 0: return '0'*(padAmount+1)
    padding = ''
    while num < 10**padAmount:
        padding += '0'
        padAmount -= 1
    if padOn == 'right': return str(num)+padding
    return padding+str(num)

#  Filesystem functions
def writeFileToZip(filePath, zipPath, compressionLevel=9, openMode='a'): #Compresses the file to a zip, using specified mode, and compression levels 0-9
    print ('Compressing:\n'+filePath+' >'+str(compressionLevel)+'> '+zipPath)
    zf = zipfile.ZipFile(zipPath, openMode, zipfile.ZIP_DEFLATED, compresslevel=compressionLevel)
    zf.write(filePath, os.path.relpath(filePath, os.path.split(filePath)[0]))
    zf.close()
def writeDirToZip(dirPath, zipPath, compressionLevel=9, openMode='a'):
    print ('Compressing dir:\n'+dirPath+' >'+str(compressionLevel)+'> '+zipPath)
    zf = zipfile.ZipFile(zipPath, openMode, zipfile.ZIP_DEFLATED, compresslevel=compressionLevel) #Creates a new zip file at the specified path
    for root, dirs, files in os.walk(dirPath): #Walks through the directory
        for file in files:
            zf.write(root+'/'+file, os.path.relpath(root+'/'+file, dirPath)) #Writes all the files in the directory individually to the zip file
    zf.close()
def closeOpenFileHandles():
    print ('Closing open file handles for process '+str(os.getpid())+'...')
    p = psutil.Process(os.getpid()) #Gets the working process (AKA this one)
    for handle in p.open_files(): #Close all open file handles
        try:
            if handle.fd != -1:
                os.close(handle.fd) #Close the handle
                print ('Closed '+str(handle))
        except:
            print ('Error! Unable to close file handle '+str(handle)+'\n'+traceback.format_exc())
    print ('Closed all open file handles')

#   Get file from server
def getFileFromServer(url, encoding=None):
    print ('GET >'+url+'< [encoding='+str(encoding)+']')
    r = requests.get(url)
    if encoding != None: r.encoding = encoding
    r.close()
    return r.text

#  Subprocess functions
inputQueue = deque()
def getOutput(process): #Prints all of the process' buffered STDOUT (decoded it from UTF-8) and also returns it
    try:
        data = process.stdout.readline().decode('UTF-8', 'replace').rstrip()
        print (data)
    except UnicodeDecodeError:
        print ('Unable to decode unicode character from target STDOUT!')
        data = False
    else:
        try:
            parseOutput(data)
        except:
            print ('An error occured while parsing!\n'+traceback.format_exc())
    if inputQueue: #Inject output & automatically parse it
        nxt = inputQueue.popleft() #Get the earliest added item
        parseOutput(nxt)
    sys.stdout.flush()
    return data

# Get username for Ubuntu
if os.name != 'nt': bashUser = runWOutput('logname').rstrip()

# Fix cache dir (if missing)
if not os.path.exists(cacheDir): os.mkdir(cacheDir)

# Auto-update
def getVersion():
    if not os.path.exists(cacheDir+'Version.txt'): currentID = -1.0
    else:
        with open(cacheDir+'Version.txt') as f:
            try:
                currentID = float(f.read().rstrip())
            except:
                currentID = -1.0
    return currentID
def autoUpdate():
    print ('Checking for a new release...')
    latestRelease = json.loads(getFileFromServer('https://api.github.com/repos/Tiger-Tom/RunServerDotPy/releases/latest'))
    latestID = float(latestRelease['tag_name'].replace('v', ''))
    currentID = getVersion()
    print ('Current release: '+str(currentID))
    print ('Newest availiable release: '+str(latestID))
    if currentID >= latestID:
        print ('You already have the latest version availiable!')
        return
    if input('Update to "'+latestRelease['name']+'" ('+str(latestID)+') (released '+latestRelease['published_at']+') ? (Y/n) >').lower() == 'n': return
    if input('Show version information? (y/N) >').lower() == 'y': print (latestRelease['body'])
    print ('Fetching update and installing...')
    downloadURL = json.loads(getFileFromServer(latestRelease['assets_url']+'?RunServer.py'))[0]['browser_download_url']
    if input('Is this the correct file? '+sys.argv[0]+' (Y/n) >').lower() == 'n': raise Exception
    print (downloadURL+' --> '+sys.argv[0])
    with requests.Session() as s:
        update = s.get(downloadURL)
        with open(sys.argv[0], 'w', encoding='UTF-8') as f:
            for i in update.iter_lines():
                f.write(i.decode('UTF-8')+'\n')
    print ('Update written')
    print ('Writing version tag...')
    with open(cacheDir+'Version.txt', 'w') as f:
        f.write(str(latestID))
    print ('Closing self to open new version...')
    try:
        finalizeLogFile() #Finalize the log file
    except:
        print ('Couldn\'t finalize log file-it probably hasn\'t been made yet')
    closeOpenFileHandles() #Important, because command below leaves file handles open
    print ('Goodbye')
    os.execl(sys.executable, sys.executable, *sys.argv)
autoUpdate()

# Configuration

#  Set config defaults
if not os.path.exists(confDir): os.mkdir(confDir)
ccRootUsr = '§server console__'
ccWebIUsr = '§web interface console__'
confFiles = { #'[name].conf': '[default contents]',
    'admins.conf': ccRootUsr+'\n'+ccWebIUsr,
    'motds.conf': 'Minecraft Server (Version {%VERSION})',
    'serverVersion.conf': 'Configure this in serverVersion.conf!',
    'ramInMB.conf': '1024',
    'chatCommandPrefix.conf': ';',
    'tempUnit.conf': 'c',
    'emoticons.conf': 'https://raw.githubusercontent.com/Tiger-Tom/RunServerDotPy-extras/main/DefaultConfig/emoticons.conf',
    'userJoinMSG.conf': 'https://raw.githubusercontent.com/Tiger-Tom/RunServerDotPy-extras/main/DefaultConfig/userJoinMSG.conf',
}
for i in confFiles:
    if not os.path.exists(confDir+i):
        with open(confDir+i, 'w', encoding='UTF-16') as cf:
            if (confFiles[i].startswith('https://')) or (confFiles[i].startswith('http://')):
                r = requests.get(confFiles[i])
                cf.write(r.text)
                r.close()
            else: cf.write(confFiles[i]) #Write defaults if missing
        
#  Read configs
def loadConfiguration():
    print ('Loading configuration...')
    global admins, srvrVersionTxt, motds, ramMB, chatComPrefix, tempUnit, emoticons, userJoinMSG
    with open(confDir+'admins.conf', encoding='UTF-16') as f:
        admins = set(f.read().split('\n')) #Usernames of server administrators, who can run "sudo" commands (in a set, since it is faster because sets are unindexed and unordered)
    with open(confDir+'serverVersion.conf', encoding='UTF-16') as f:
        srvrVersionTxt = f.read().rstrip()
    with open(confDir+'motds.conf', encoding='UTF-16') as f:
        motds = f.read().rstrip().replace('{%VERSION}', srvrVersionTxt).split('\n') #List of MOTDs (single line only, changes every server restart)
    with open(confDir+'ramInMB.conf', encoding='UTF-16') as f:
        ramMB = int(f.read().rstrip())
    with open(confDir+'chatCommandPrefix.conf', encoding='UTF-16') as f:
        chatComPrefix = f.read().rstrip()
    with open(confDir+'tempUnit.conf', encoding='UTF-16') as f:
        tempUnit = f.read().lower()
        if tempUnit.startswith('c'): tempUnit = [0, '°C']
        elif tempUnit.startswith('f'): tempUnit = [1, '°F']
        elif tempUnit.startswith('k'): tempUnit = [1, 'K']
        else: raise Exception('Unknown temperature unit "'+tempUnit+'"! Must be "c" or "f" or "k"!')
    with open(confDir+'emoticons.conf', encoding='UTF-16') as f:
        e = f.read().rstrip().split('\n')
        emoticons = {}
        e = e[1:]
        pageName = 'Default Page'
        for i in e:
            if (len(i) == 0) or i.startswith('#'): pass
            elif i.startswith('%'):
                pageName = i[1:].lower()
                emoticons[pageName] = [i[1:]]
            elif i.startswith('&'): emoticons[pageName].append(tuple(i)[1:])
            else: emoticons[pageName].append(i)
    with open(confDir+'userJoinMSG.conf', encoding='UTF-16') as f:
        userJoinMSG = f.read()
    print ('Configuration loaded')
loadConfiguration()

#  Load icons
#(icons change every server restart, and must be 64*64 pixel PNGs. They can be named anything)
if not os.path.exists(iconsDir): os.mkdir(iconsDir) #Fix if missing
serverIcons = []
for i,j,k in os.walk(iconsDir): #Find all *.png's in the icon directory
    for l in k:
        if l.endswith('.png'): serverIcons.append(i+l)
        else: print ('Warning: a non-png file is in the icons directory:\n'+i+l)
print ('Server MOTDs:\n'+(', '.join(motds)))

# Command generation
mainCommand = 'java -jar -Xms'+str(ramMB)+'M -Xmx'+str(ramMB)+'M "'+srvrFolder+'server.jar" nogui'

# Logging
logFiles = ['Chat', 'RawChat', 'ChatCommands', 'Profanity', 'Unusual+Errors', 'WebInterface']
loggedAmountTotal = {} #Total amount of logs collected
loggedAmountIter = {} #Amount of logs collected since last finalized log
logFileHandles = {}

#  Logging functions
def makeLogFile(): #Setup the log file
    global logStartTime
    t = time.localtime()
    if not os.path.exists(logDir): os.mkdir(logDir) #Fix logging directory if it doesn't exist
    logStartTime = time.strftime('%Y;%m;%d;%H;%M').split(';')
def finalizeLogFile(lost=False): #Finish the log file and save it
    global loggedAmountIter
    global logFileHandles
    #Repair missing dirs
    if not os.path.exists(totalLogDir): os.mkdir(totalLogDir) #Repair missing total log dir
    if lost and not os.path.exists(logDir+'Lost/'): os.mkdir(logDir+'Lost/') #Repair missing lost log dir ONLY if saving a lost log
    #Close open log file handles
    for i in logFileHandles.keys():
        print ('Closing log file handle for "'+i+'"...')
        try:
            logFileHandles[i].close()
        except:
            print ('Could not close log file handle for "'+i+'" because\n'+traceback.format_exc())
    #Make file name
    if lost: targetDir = logDir+'Lost/FOUND_ON_'+time.strftime('%Y-%m-%d_%H-%M-%S')+'.zip'
    else:
        curTime = time.strftime('%Y;%m;%d;%H;%M').split(';')
        targetDir = logDir+('-'.join(logStartTime[0:3]))+'_'+('-'.join(logStartTime[3:]))+'__'
        if logStartTime[2] == curTime[2]: indx = 2 #Year is the same, so recording it is unneeded
        else: indx = 3
        targetDir += '-'.join(curTime[0:indx])+'_'+('-'.join(curTime[indx:]))+'.zip'
    #Don't save something if nothing is logged
    if (loggedAmountIter == {}) and not lost:
        print ('Not saving log file, as there is nothing to save!')
        return False
    if lost: print ('Saving lost log...')
    else:
        print ('Logs collected since last save:\n'+str(loggedAmountIter))
        print ('Logs collected since last RunServerDotPy restart:\n'+str(loggedAmountTotal))
        loggedAmountIter = {}
    #Save to main log
    print ('Compressing and saving main log...')
    writeDirToZip(logDir+'latest/', targetDir)
    #Append to total log
    for i in logFiles:
        if os.path.exists(logDir+'latest/'+i+'.txt'):
            newFN = logDir+'latest/'+os.path.splitext(os.path.basename(targetDir))[0]+'.txt'
            shutil.copy(logDir+'latest/'+i+'.txt', newFN)
            writeFileToZip(newFN, totalLogDir+i+'.zip')
            print ('Wrote "'+i+'" to total log files')
    #Cleanup
    shutil.rmtree(logDir+'latest/') #Remove old logs
    if os.name != 'nt': #Change ownership, since RunServerDotPy must be run as sudo on Linux distributions, as "server.jar" also has to be run as root
        print ('Changing owner/permissions of '+srvrFolder+'/RunServerDotPy...')
        print ('sudo chown -R '+bashUser+' '+srvrFolder+'/RunServerDotPy')
        os.system('sudo chown -R '+bashUser+' '+srvrFolder+'/RunServerDotPy')
def logData(data, category): #Adds data to the specified log
    global logFileHandles
    global loggedAmountTotal
    global loggedAmountIter
    try: #Grab the file handle if it's already open for faster I/O times
        lfHandle = logFileHandles[category]
        lfHandle.write(time.strftime('[%Y-%m-%d %H:%M:%S] ')+data.rstrip()+'\n')
    except (ValueError, KeyError): #File handle never made or does not exist #Make sure not to catch the wrong exceptions
        if not os.path.exists(logDir+'latest/'): os.mkdir(logDir+'latest/')
        lfHandle = open(logDir+'latest/'+category+'.txt', 'a+', encoding='UTF-16')
        logFileHandles[category] = lfHandle
        lfHandle.write(time.strftime('>>[NEW HANDLE OPENED]<<\n[%Y-%m-%d %H:%M:%S] ')+data.rstrip()+'\n')
        print ('Initialized log file for "'+category+'"')
    lfHandle.flush() #Flush to save the changes
    try:
        loggedAmountTotal[category] += 1
    except KeyError:
        loggedAmountTotal[category] = 1
    try:
        loggedAmountIter[category] += 1
    except KeyError:
        loggedAmountIter[category] = 1

#  Fix "latest" log dir if it doesn't exist
if os.path.exists(logDir+'latest/'): finalizeLogFile(True)

#  Initialize log file
makeLogFile()

# Minecraft server utilities

#  Commands
def writeCommand(cmd): #Writes "cmd" to the process' STDIN and adds '\n' to make it run, while also encoding it in UTF-8
    try:
        if process.poll() == None:
            process.stdin.write((cmd+'\n').encode('UTF-8'))
            process.stdin.flush()
        else: raise NameError
    except NameError: #If no process exists
        print ('Cannot write command, as process has been stopped')
#   Tellraw
def safeTellRaw(text, addQuotes=True):
    #return json.dumps(text.rstrip()) #Formats a string to be safe for use in a tellraw command
    text = text.replace('\\', '\\\\').replace('"', '\\"').replace('\'', '\\\'')
    if addQuotes: return '"'+text+'"'
    return text
def tellRaw(text, frmTxt=None, to='@a'): #Runs the tellraw commands, and adds a "from" text if frmTxt is not None (with a from text would look like: <"frmTxt"> "text")
    if (to == ccRootUsr) or (ccRootUsr in str(frmTxt)):
        if frmTxt != None: print (frmTxt+' > "'+text+'"')
        else: print (' > "'+text+'"')
        return
    elif (to == ccWebIUsr) or (ccWebIUsr in str(frmTxt)):
        if frmTxt != None: web_data.append(frmTxt+' > "'+text+'"')
        else: print (' > "'+text+'"')
        return
    text = text.split('\n')
    if frmTxt != None:
        for i in text:
            writeCommand('tellraw '+to+' ["<'+frmTxt+'> ",'+safeTellRaw(i)+']')
            print ('"'+frmTxt+'" > "'+i+'" > "'+to+'"')
    else:
        for i in text:
            writeCommand('tellraw '+to+' '+safeTellRaw(i))
            print (' > "'+i+'" > "'+to+'"')

#  Output parsing
def parseOutput(line): #Parses the output, running subfunctions for logging and parsing chat, as well as setting variables for web interface if it exists
    if webInterfaceAuth != None: web_data.append(line)
    if len(line) == 0: print ('Not parsing empty line (length 0)') #In case of empty line
    elif line[0] != '[': logData(line, 'Unusual+Errors') #There is no [HH:MM:SS] in front of message, which is unusual
    elif (line[9:12] == '] [') and (line[11:].split('/')[1][:5] in {'ERROR', 'FATAL'}): logData(line, 'Unusual+Errors') #It's an error!
    elif (line[9:12] == '] [') and (line[33:42] == '<--[HERE]'): return #Blank command written, ignore
    elif (line[33] in {'*', '<', '['}) and (parseChat(line)[0] != 0): #The first one is checked first, since it uses up less resources, and any chat message has to have either a < or a * or a [
        chatL = parseChat(line)
        if chatL[0] != 0: #It is a chat message of some sort (either chat, /me, or /say)
            logData(line, 'RawChat') #Save line directly to raw chat log
            if chatL[0] == 1: #Is a regular chat message
                logData('"'+chatL[1]+'" said "'+chatL[2]+'"', 'Chat') #Save formatted chat to chat log: "[User]" said "[Message]"
                if chatL[2].startswith(chatComPrefix): #If it is a ChatCommand
                    logData('"'+chatL[1]+'" tried to run "'+chatL[2]+'"', 'ChatCommands')
                    parseChatCommand(chatL[1], chatL[2])
            elif chatL[0] == 2: logData('"'+chatL[1]+'" /me\'d "'+chatL[2]+'"', 'Chat') #Is a /me message, save it in the chat log formatted like: "[User]" /me'd "[Message]"
            elif (chatL[0] == 3) and (not chatL[1] == 'Server'): logData('"'+chatL[1]+'" /said "'+chatL[2]+'"', 'Chat') #Is a /say message, save it in the chat log formatted like: "[User]" /said "[Message]"
        if profanity.contains_profanity(chatL[1]): #Chat message potentially contains profanity, warn user and log it
            tellRaw('<'+chatL[0]+'> '+profanity.censor(chatL[1], '!'))
            tellRaw('Potential profanity detected and logged', '[Swore!]')
            logData(line, 'Profanity')
    #0         1         2         3         4
    #01234567890123456789012345678901234567890123456789
    #[14:56:06] [Server thread/INFO]: TigerTom joined the game
    #[14:56:01] [Server thread/INFO]: TigerTom left the game
    elif (line[9:33] == '] [Server thread/INFO]: ') and (line[42:] == 'joined the game'): #A player joined the game
        usrJoined = line.split(' ')[3]
        writeCommand('tellraw @a '+userJoinMSG.replace('{%USER}', usrJoined).rstrip().lstrip())
        tellRaw('Use "'+chatComPrefix+'help" for a list of ChatCommands!', None, usrJoined)
    elif (line[9:33] == '] [Server thread/INFO]: ') and (line[42:] == 'left the game'): #A player left the game
        global chatCommandsLastUsed
        usrLeft = line.split(' ')[3]
        try:
            del chatCommandsLastUsed[usrLeft] #Remove the user from the spam protection timing if they leave to save memory
            print ('Removed user from chatCommandsLastUsed: '+usrLeft)
        except KeyError: #If the user didn't use any ChatCommands
            pass
    #0         1         2         3         4         5         6
    #0123456789012345678901234567890123456789012345678901234567890
    #[16:00:26] [Server thread/INFO]: [TigerTom: Added tag 'test' to TigerTom]
    elif (line[9:33] == '] [Server thread/INFO]: ') and (line[33] == '[') and ('Added tag \'_rs.py_chatCommand_flag.' in line[34:].split(']')[0]):
        cc_parseTagFlag(line.split('\'_rs.py_chatCommand_flag.')[1].split('\'')[0], line[34:].split(' ')[0][:-1])
def parseChat(line): #Get the chat / /me / /say message and username out of a console line
    #Returns ["0 if not chat, 1 if chat, 2 if /me, 3 if /say", "username (if present)", "message (if present)"]
    #+10:             1         2         3
    #Index: 0123456789012345678901234567890123456789
    #Chat:  [HH:MM:SS] [Server thread/INFO]: <Username> Message
    #/me:   [HH:MM:SS] [Server thread/INFO]: * Username Message
    #Death: [HH:MM:SS] [Server thread/INFO]: Username was slain by Entity Name
    if line[0] == '[' and line[9] == ']': #Check for [HH:MM:SS]
        if line[11:33] == '[Server thread/INFO]: ': #Check for [Server thread/INFO]: 
            if (line[33] == '<') and (line[33:36] != '<--'): #It is a chat message!
                line = line[34:].split('> ')
                username = line[0]
                message = '> '.join(line[1:])
                return [1, username, message]  #1=it is a chat message
            elif line[33] == '*': #It is a /me message! (Who actually uses those???)
                line = line[35:].split(' ')
                username = line[0]
                message = ' '.join(line[1:])
                return [2, username, message] #2=it is a /me message
            elif line[33] == '[': #It may be a /say
                if not ' ' in line[33:].split(']')[0]: #If there is a space there, then it is a command and not a /say
                    line = line[34:].split('] ')
                    username = line[0]
                    message = '] '.join(line[1:])
                    return [3, username, message] #3=it is a /say message
    return [0] #0=not a chat or /me or /say message

# ChatCommands

#  Variables
chatCommandsLastUsed = {}

#   Help variables (help text keys in-game will be organized by the order by they are defined)
def updateHelp():
    newHelp = getFileFromServer('https://raw.githubusercontent.com/Tiger-Tom/RunServerDotPy-extras/main/Help/ChatCommandsHelp.json')
    if os.path.exists(cacheDir+'ChatCommandsHelp.json'): #Compare current help fingerprint with newest help version fingerprint if the current file exists
        print ('Comparing fingerprint of current version and downloaded version...')
        with open(cacheDir+'ChatCommandsHelp.json') as f:
            oldHash = md5(f.read().encode()).hexdigest()
        newHash = md5(newHelp.encode()).hexdigest()
        print (oldHash+'\n'+newHash)
        if oldHash == newHash:
            print ('Fingerprints match, no update necessary')
            loadHelp()
            return
        else: print ('Fingerprints do not match. An update is necessary')
    else: print ('Help file does not exist. An update is necessary')
    with open(cacheDir+'ChatCommandsHelp.json', 'w') as f:
        f.write(newHelp)
    print ('Help updated')
    loadHelp()
def loadHelp():
    global chatCommandsHelp,chatCommandsHelpAdmin,chatCommandsHelpRoot
    with open(cacheDir+'ChatCommandsHelp.json') as f:
        chatCommandsHelp,chatCommandsHelpAdmin,chatCommandsHelpRoot = json.load(f) #Load ChatCommands help from cached JSON file
updateHelp()

#  Functions
def parseChatCommand(user, data):
    data = data.split(' ')
    cmd = data[0][1:].lower()
    args = data[1:]
    if cmd in {'root', 'sudo'} and len(args) > 0: #The command is not a normal-level command (a {} is a set, which saves time for something like this because it is unordered and unindexed)
        print (user+' is trying to run '+cmd+'-level ChatCommand "'+args[0]+'" with '+str(len(args[1:]))+' arguments')
        comm = args[0].lower()
        args = args[1:]
        if cmd == 'root': #The command is a root-level command (only server console can run)
            if user == ccRootUsr: runRootChatCommand(comm, args) #User has permissions, run command
            else: #User does not have permissions, kick them from the server
                tellRaw('Root access denied, '+user+'. You do not have access level "root"!', 'Firewall')
                writeCommand('kick '+user+' Root access denied, '+user+'. You do not have access level "root"!')
        else: #Administrator command, 
            if user in admins: runAdminChatCommand(comm, args, user) #User has permissions, run command
            else: #User does not have permissions, kick them from the server
                tellRaw('SuperUser access denied, '+user+'. You do not have access level "admin"!', 'Firewall')
                writeCommand('kick '+user+' SuperUser access denied, '+user+'. You do not have access level "admin"!')
    else:
        chatCommandsLastUsed.setdefault(user, 0)
        if time.monotonic()-chatCommandsLastUsed[user] < 1: writeCommand('kick '+user+' SpamProtection: Please wait 1 second between ChatCommands')
        else: runChatCommand(cmd, args, user)
        if not user in admins: chatCommandsLastUsed[user] = time.monotonic() #User is not an admin, so reset their timer


#   Load ChatCommand mods
def loadMods():
    global chatCommandsHelp,chatCommandsHelpAdmin,chatCommandsHelpRoot,modsRegular,modsAdmin,modsRoot,customRuntimes
    modsRegular = {}
    modsAdmin = {}
    modsRoot = {}
    customRuntimes = {'firstStart': [], 'everyStart': [], 'lastStop': [], 'everyStop': []}
    loadedMods = []
    if not os.path.exists(modDir): #Check if the mod directory exists and create it if it doesn't
        print ('Mods dir doesn\'t exist, creating one now...')
        os.mkdir(modDir)
    modFiles = [f for f in os.listdir(modDir) if os.path.isfile(modDir+'/'+f)] #Find all files in the mod directory
    if not len(modFiles): #If no files/mods were found
        print ('No mods found')
        return False
    print ('Loading '+str(len(modFiles))+' mod file(s)...')
    load_mod = None
    successes = 0
    for i in modFiles: #Load all mods
        try:
            with open(modDir+'/'+i) as f:
                print ('Loading mod file '+i+'...')
                exec(f.read()) #Read & parse mod
                print ('Checking if mod has an initscript...')
                if load_mod != None:
                    print ('Mod has an initialization function. Executing...')
                    try:
                        init_mod([chatCommandsHelp, chatCommandsHelpAdmin, chatCommandsHelpRoot], [modsRegular, modsAdmin, modsRoot])
                        successes += 1
                    except Exception as e: print ('An error occured while loading initscript for mod of file "'+i+'"\nSome changes to ChatCommands and help texts may have still been applied\n [Exception]: "'+str(e)+'"')
                print ('Checking if mod has a custom runtime staging script...')
                if inject_custom_mod_runtime != None:
                    print ('Mod has a custom runtime stager function. Executing...')
                    try:
                        newRuntimeMods = inject_custom_mod_runtime(globals)
                        for j in newMods:
                            print ('Adding new mod to runtime "'+j+'"')
                            if j in customRuntime: customRuntime[j] += newRuntimetime[j]
                        successes += 1
                    except Exception as e: print ('An error occured while modifying or loading new runtimes for mod of file "'+j+'"\nSome changes to runtime may have still been applied\n [Exception]: "'+str(e)+'"')
                print ('Finished loading mod file '+i)
        except Exception as e: print ('Couldn\'t load mod file '+i+' because:\n'+str(e))
    print ('Finished loading '+str(len(modFiles))+' mod file(s) ('+str(successes)+' successful initscripts and custom runtime applications)')
loadMods()

#  ChatCommands

#   Basic/User-level ChatCommands (any user can run)
def runUserCCommand(cmd, user):
    if len(modsRegular) and (cmd.split()[0] in modsRegular): #Check for any modded ChatCommands, if there are any then check if any of them match the ChatCommand, and execute the modded ChatCommand if so.
        modsRegular[cmd.split()[0]](cmd.split()[1:], user)
        return
    match cmd.split():
        # Prefix privelege-escalating commands
        case ['sudo', *sCmd]: #Runs "super-user" commands that can only be run by players specified in admins.conf
            runSudoCommand(sCmd, user)
        case ['root', *rCmd]: #Runs "root" commands that only those with access to the physical server console can run
            runRootCommand(rCmd)
        # Misc commands
        case ['help', *args]: #Displays a list of all commands along with aliases and basic syntax, or give information on a single command if an argument is specified
            cc_help(chatCommandsHelp, args, user=user)
        case ['emoticons', *args]: #Starts a new thread to show either a list of all emoticon pages to the player, or a list of copyable emoticons that are in a specified page
            threading.Thread(target=cc_tellrawEmoticons, args=(user,args), daemon=True).start()
        case ['nuke']: #Basically just crashes the player's game
            threading.Thread(target=cc_crashPlayer, args=(user, 1), daemon=True).start()
        # MC server information commands
        case ['size']: #Displays the size of the server's world folder
            size = 0
            for p, d, f in os.walk(srvrFolder+'world/'): #Calculate size
                for i in f:
                    size += os.path.getsize(p+i)
            tellRaw('The server world folder is '+parseMadeValues(makeValues(size, 1024, sizeVals))+' large', 'Size', user)
        case ['tps']: #Run the Minecraft "debug" command for 10 seconds, which outputs the TPS when complete
            global lastTickTest
            timeSinceLast = round(time.monoronic())-lastTickTest
            if (timeSinceLast > 120) or (user in admins and timeSinceLast > 15): #Checks when the last test was run, in order to prevent misuse
                lastTickTest = round(time.monotonic()) #Reset the timer
                tellRaw('Beginning asynchronous TPS test...\nThis should take about 10 seconds', 'TPS')
                writeCommand('debug start') #Initialize the debug
                threading.Thread(target=funcWithDelay, args=(10, writeCommand, ('debug stop',)), daemon=True).start() #Start a new thread that will inject the command to stop the debugging after 10 seconds
                while True: #This is required to keep processing output, since this should be on the main thread
                    out = getOutput(process)
                    if (out[0] == '[') and (out[9:48] == '] [Server thread/INFO]: Stopped tick pr'): #This text will show up when the above command injects the debug stopping command, and has the information needed
                        out = out[62:].split(' ')
                        tellRaw('The test lasted for '+out[0]+' seconds ('+out[3]+' ticks)\nRunning at about '+out[5][1:]+' ticks per second (should be around 20)', 'TPS')
                        return
            else: tellRaw('Please wait '+parseMadeValues(makeValues(120-timeSinceLast, 60, timeVals))+' to run another TPS test', 'TPS')
        # Server system information commands
        case ['speedtest']: #Runs an internet speed test asynchronously and outputs the result when it's complete
            global lastSpeedTest
            timeSinceLast = round(time.monotonic())-lastSpeedTest
            if (timeSinceLast > 600) or (user in admins): #Checks when the last was performed in order to prevent misuse
                tellRaw('Beginning speed test... (This could take a while)', 'SpeedTest')
                asyncRunWCallback(cc_parseSpeedTest, 'speedtest-cli --json', lambda cbF, cmd: tellRaw('An error occured while running the speed test', 'SpeedTest'))
            else: tellRaw('Please wait '+parseMadeValues(makeValues(600-timeSinceLast, 60, timeVals))+' to run another speed test', 'SpeedTest')
        case ['sysinfo'] | ['info']: #Get some kinds of system information, such as 
            tellRaw('System information for '+platform.node()+':', 'SysInf', user)
            tellRaw(str(psutil.cpu_percent())+'% CPU usage\n'+str(psutil.virtual_memory().percent)+'% memory used', None, user)
            temps = psutil.sensors_temperatures()
            for i,j in psutil.sensors_temperatures().items():
                t = 0
                for k in j:
                    t += k
                t = t/len(j)
                if tempUnit[0] == 2: t += 273.15 #Convert to kelvin if needed
                elif tempUnit[0] == 1: t = (t*(9/5))+32 #Convert to Fahrenheit if needed
                tellRaw('Average temperature "'+i+'" is '+str(t)+tempUnit[1], None, user)
            tellRaw('The disk has had a total of '+parseMadeValues(makeValues(psutil.disk_io_counters().read_bytes, 1024, sizeVals))+' read and '+parseMadeValues(makeValues(psutil.disk_io_counters().write_bytes, 1024, sizeVals))+' written since the last system restart', None, user)
        case ['uptime']: #Shows how long the server and system have each been running
            tellRaw('The server has been online for '+parseMadeValues(makeValuesDiffDelimiter(round(time.time()-uptimeStart), [60, 60, 24, 7], longTimeVals)), 'Uptime', user) #How much time the server has been online for since last restart (formatted with makeValues)
            tellRaw('(Online since '+(time.ctime(uptimeStart).rstrip().replace('  ', ' '))+')', None, user) #The formatted date and time of the last server restart
            tellRaw('The system has been powered on for '+parseMadeValues(makeValuesDiffDelimiter(round(time.time()-psutil.boot_time()), [60, 60, 24, 7], longTimeVals)), 'Uptime', user) #How much time the system has been powered on (formatted with makeValues)
            tellRaw('(Powered on since '+(time.ctime(psutil.boot_time()).rstrip().replace('  ', ' '))+')', None, user) #The formatted date and time of the last system power on
        case ['wiki' | 'github']: #Shows links to the wiki and GitHub page for RunServerDotPy
            # Commands below display the text that is above them ({x} = link)
            # GitHub Pages: {GitHub Repository} | {Changelog}
            # {All Releases} | {Latest Release} | {Credits}
            writeCommand('tellraw '+user+' ["",{"text":"GitHub Pages","bold":true,"underlined":true},": ",{"text":"GitHub Repository","underlined":true,"color":"dark_blue","clickEvent":{"action":"open_url","value":"https://github.com/Tiger-Tom/RunServerDotPy"},"hoverEvent":{"action":"show_text","contents":["https://github.com/Tiger-Tom/RunServerDotPy"]}}," | ",{"text":"Changelog","underlined":true,"color":"dark_blue","clickEvent":{"action":"open_url","value":"https://github.com/Tiger-Tom/RunServerDotPy/blob/main/Changelog.md"},"hoverEvent":{"action":"show_text","contents":["https://github.com/Tiger-Tom/RunServerDotPy/blob/main/Changelog.md"]}},"\n",{"text":"All Releases","underlined":true,"color":"dark_blue","clickEvent":{"action":"open_url","value":"https://github.com/Tiger-Tom/RunServerDotPy/releases"},"hoverEvent":{"action":"show_text","contents":["https://github.com/Tiger-Tom/RunServerDotPy/releases"]}}," | ",{"text":"Latest Release","underlined":true,"color":"dark_blue","clickEvent":{"action":"open_url","value":"https://github.com/Tiger-Tom/RunServerDotPy/releases/latest"},"hoverEvent":{"action":"show_text","contents":["https://github.com/Tiger-Tom/RunServerDotPy/releases/latest"]}}," | ",{"text":"Credits","underlined":true,"color":"dark_blue","clickEvent":{"action":"open_url","value":"https://github.com/Tiger-Tom/RunServerDotPy-extras/blob/main/Credits.md"},"hoverEvent":{"action":"show_text","contents":["https://github.com/Tiger-Tom/RunServerDotPy-extras/blob/main/Credits.md"]}}]')
            # Wiki: {Main Page}
            # {General ChatCommand Info}
            # {ChatCommand List+Info}
            writeCommand('tellraw '+user+' ["",{"text":"Wiki","bold":true,"underlined":true},": ",{"text":"Main Page","underlined":true,"color":"dark_blue","clickEvent":{"action":"open_url","value":"https://github.com/Tiger-Tom/RunServerDotPy/wiki"},"hoverEvent":{"action":"show_text","contents":["https://github.com/Tiger-Tom/RunServerDotPy/wiki"]}},"\n",{"text":"ChatCommand List+Info","underlined":true,"color":"dark_blue","clickEvent":{"action":"open_url","value":"https://github.com/Tiger-Tom/RunServerDotPy/wiki/ChatCommands"},"hoverEvent":{"action":"show_text","contents":["https://github.com/Tiger-Tom/RunServerDotPy/wiki/ChatCommands"]}},"\n",{"text":"User-Level ChatCommands","underlined":true,"color":"dark_blue","clickEvent":{"action":"open_url","value":"https://github.com/Tiger-Tom/RunServerDotPy/wiki/ChatCommands-(User-level)"},"hoverEvent":{"action":"show_text","contents":["https://github.com/Tiger-Tom/RunServerDotPy/wiki/ChatCommands-(User-level)"]}}]')
            # {Sudo-level ChatCommands}   (ONLY SHOWS IF USER IS AN ADMIN!)
            if user in admins: writeCommand('tellraw '+user+' {"text":"Sudo ChatCommand List+Info","underlined":true,"color":"dark_blue","clickEvent":{"action":"open_url","value":"https://github.com/Tiger-Tom/RunServerDotPy/wiki/ChatCommands-(Sudo-level)"},"hoverEvent":{"action":"show_text","contents":["https://github.com/Tiger-Tom/RunServerDotPy/wiki/ChatCommands-(Sudo-level)"]}}')
        # Catch-all
        case _:
            tellRaw('You did not type in any recognized command. Try "'+chatComPrefix+'help"?', None, user)

#   Sudo/admin ChatCommands (only users specified in admins.conf may run these)
def runSudoCCommand(cmd, user):
    if len(modsAdmin) and (cmd.split()[0] in modsAdmin): #Check for any modded ChatCommands, if there are any then check if any of them match the ChatCommand, and execute the modded ChatCommand if so.
        modsAdmin[cmd.split()[0]](cmd.split()[1:], user)
        return
    match cmd.split():
        # Misc commands
        case ['help', *args]: #Displays a list of all super-user commands, or information on matching commands if an argument is given
            cc_help(chatCommandsHelpAdmin, args, chatComPrefix+'sudo', user)
        case ['logs', *args]: #Displays how many logs have been taken, either since the last time the program restarted if "total" argument is specified, otherwise shows how many logs have been taken since the last server restart
            if 'total' in args: tellRaw('Logs collected over '+str(restarts)+' restarts:\n'+str(loggedAmountTotal), 'Logs', user)
            else: tellRaw('Logged amount since '+time.ctime(uptimeStart).rstrip()+':\n'+str(loggedAmountIter), 'Logs', user)
        # RunServerDotPy commands
        case ['reconfig']: #Reloads all of RunServerDotPy's configuration
            tellRaw('Reloading configuration...', 'Config', user)
            loadConfiguration()
            tellRaw('Done', 'Config', user)
        case ['refresh']: #Restarts RunServerDotPy completely - any changes made to the program will be implemented
            tellRaw('Refreshing server...', user)
            runSudoCCommand('stop', [], user) #Manually calls the "stop" admin ChatCommand with
            print ('Unhooking keyboard...')
            keyboard.unhook_all()
            while process.poll() == None: #Get and parse remaining output until the process is done running
                getOutput(process)
            try:
                process.wait() #Wait for the process to complete
                print (process.stdout.read().decode('UTF-8', 'replace')) #Read and display any leftover messages and flush buffer
            except: pass
            finalizeLogFile() #Finalize the log file
            closeOpenFileHandles() #Important because the process replace command will leave trailing/open file handles
            print ('Goodbye')
            os.execl(sys.executable, sys.executable, *sys.argv) #Immediately replace the current process with this one, whilst still retaining any arguments
        case ['remod']: #Reloads all mods
            tellRaw('Reloading mods...', 'Mods', user)
            loadMods() #Unloads all loaded mods and then loads all mods again
            tellRaw('Done', 'Mods', user)
        # Server controls
        case ['reload']: #Reloads the server (equivalent to /reload, reloads all datapacks)
            tellRaw('Reloading!', None, user)
            writeCommand('reload')
        case ['restart' | 'stop']: #Stops the Minecraft server (using /stop) (the program, by default, automatically starts the server again if it closes)
            tellRaw('Restarting server...', user)
            for i in range(3, 1, -1): #Countdown from 3-2 to warn users
                writeCommand('tellraw @a ["",{"text":"The server is going down for a restart in ","color":"red"},{"text":"'+str(i)+'","bold":true,"color":"red"},{"text":" seconds!","color":"red"}]')
                time.sleep(1)
            writeCommand('tellraw @a ["",{"text":"The server is going down for a restart in ","color":"red"},{"text":"1","bold":true,"color":"red"},{"text":" second!","color":"red"}]') #Final 1 second of countdown
            time.sleep(1)
            writeCommand('tellraw @a ["",{"text":"The server is going down for a restart ","bold":true,"color":"red"},{"text":"NOW!","bold":true,"color":"dark_red"}]')
            writeCommand('kick @a Server restarting!') #Remove all players from the game
            writeCommand('save-all') #Save the game
            writeCommand('stop') #Stop the server
        case ['save' | 'save-all']: #Saves the game (equivalent to /save-all)
            tellRaw('Saving the game')
            writeCommand('save-all')
        # Player controls
        case ['ban', target, *reason]: #Bans the specified player for optional reason (equivalent to the in-game /ban command)
            if len(reason): #Run this if a reason was given
                reason = ' '.join(reason)
                writeCommand('ban '+target+' '+reason)
                tellRaw('Banned '+target+' for "'+reason, user)
            else:
                writeCommand('ban '+target)
                tellRaw('Banned '+target, user)
        case ['crash', target, *severity]: #Crash a user's game with excessive amounts of particles that only that user can see (only use if they are being really bad (AKA hacking, or worse)
            if len(severity):
                try:
                    severity = int(severity[0])
                    if severity < 1 or severity > 5: raise TypeError
                except TypeError:
                    tellRaw('Severity must be an integer between 1 and 5', 'Crasher', user)
                    return
            else: severity = 3
            tellRaw('Crashing '+target+' with severity '+str(severity), 'Crasher', user)
            threading.Thread(target=cc_crashPlayer, args=(target,severity), daemon=True).start()
        case ['kick', target, *reason]: #Kicks the specified player for optional reason (equivalent to the in-game /kick command)
            writeCommand('kick '+target+(' '+' '.join(reason)))
            if len(reason): tellRaw('Kicked '+target+' for '+(' '.join(reason)), user)
            else: tellRaw('Kicked '+target, user)
        case ['unban' | 'pardon', target]: #Unbans the specified player (equivalent to the in-game /pardon command)
            writeCommand('pardon '+target)
            tellRaw('Pardoned '+target, user)
        case ['webinterface']: #Starts a web interface on port 8080
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('localhost', 8080)) == 0: #Test if port 8080 is in use (which means that the web interface is already running)
                    global webInterfaceAuthUser
                    webInterfaceAuthUser = user
                    tellRaw('Please connect to port 8080 in your web browser to this machine', 'WebInterface', user)
                    threading.Thread(target=runWebInterfaceServer, daemon=True).start()
                else: tellRaw('The web interface is already in use, sorry. Please try again later', 'WebInterface', user)
        # Catch-all
        case _:
              tellRaw('You did not type in any recognized command. Try "'+chatComPrefix+'sudo help"?', None, user)

#   Root ChatCommands (can only be run from the shell)
def runRootCCommand(cmd):
    if len(modsRoot) and (cmd.split()[0] in modsRoot): #Check for any modded ChatCommands, if there are any then check if any of them match the ChatCommand, and execute the modded ChatCommand if so.
        modsRoot[cmd.split()[0]](cmd.split()[1:], user)
        return
    match cmd.split():
        case ['help', *args]: #Displays a list of all root commands, or information on matching commands if an argument is given
            cc_help(chatCommandsHelpRoot, args, chatComPrefix+'root', '', True)
        case ['clearlogs']: #Removes all logs
            global loggedAmountIter, loggedAmountTotal #Declare log counters as global so that we can modify them
            print ('Finishing logs so that they can be safely removed...')
            finalizeLogFile() #Finish the logs so that they can be safely removed, since this command closes any open file handles, fixes missing directories, and finishes up logs
            print ('Removing log directory...')
            shutil.rmtree(logDir) #Deletes everything in the log directory
            print ('Removing log counters...')
            loggedAmountIter = {}
            loggedAmountTotal = {}
            print ('Logs have been successfully removed\nInitializing new log...')
            makeLogFile()
        case ['py', *args]: #Runs a Python command
            com = ' '.join(args)
            print ('> "'+com+'"\n< "'+str(eval(com))+'"')
        case _: #Catch-all
            print ('You did not type in any recognized command. Try "'+chatComPrefix+'root help"?')

#  ChatCommand supplementary scripts
def cc_help(ccHelpDict, args, ccPref=chatComPrefix, user='', toConsole=False): #If "toConsole" is True, then this just prints it. Otherwise, it uses a tellraw command
    if user == ccRootUsr: toConsole = True
    if not len(args): command = None
    else: command = ' '.join(args)
    if command == None: cHelp = 'List of commands:\n("command" | "variation" ["positional arg(s) *=optional"] {"flags"}\n(Command prefix: '+ccPref+')\n(Use '+ccPref+'help [command] for help on a specific command)'
    else: cHelp = 'Help page for commands matching "'+command+'":'
    if toConsole: print (cHelp)
    else: tellRaw(cHelp, 'Help', user)
    showAll = (command == None) #Save a bit of time from calculations
    if ccPref != chatComPrefix and not ccPref.endswith(' '): ccPref += ' '
    for i in ccHelpDict.keys():
        if showAll:
            if toConsole: print (' • '+i)
            else: writeCommand('tellraw '+user+(' [" • ",{"text":"{%COMMAND_FULL}","clickEvent":{"action":"suggest_command","value":"{%COMMAND_SUGGEST}"},"hoverEvent":{"action":"show_text","contents":[{"text":"{%COMMAND_SUGGEST}","bold":true}]}}]').replace('{%COMMAND_FULL}', safeTellRaw(i, False)).replace('{%COMMAND_SUGGEST}', safeTellRaw(ccPref+i.split(' ')[0], False)))
        else:
            if command in i:
                if toConsole: print (' • '+i+': '+ccHelpDict[i])
                else: writeCommand('tellraw '+user+(' [" • ",{"text":"{%COMMAND_FULL}","clickEvent":{"action":"suggest_command","value":"{%COMMAND_SUGGEST}"},"hoverEvent":{"action":"show_text","contents":[{"text":"{%COMMAND_SUGGEST}","bold":true}]}},{"text":": {%COMMAND_DESC}","hoverEvent":{"action":"show_text","contents":[{"text":"{%COMMAND_DESC}","bold":true}]}}]').replace('{%COMMAND_FULL}', safeTellRaw(i, False)).replace('{%COMMAND_SUGGEST}', safeTellRaw(ccPref+i.split(' ')[0], False)).replace('{%COMMAND_DESC}', safeTellRaw(ccHelpDict[i], False)))
def cc_parseSpeedTest(res):
    global lastSpeedTest
    res = json.loads(res)
    down = makeValues(res['download'], 1024, sizeVals)
    up = makeValues(res['upload'], 1024, sizeVals)
    tellRaw(parseMadeValues(down)+' download', 'SpeedTest')
    tellRaw(parseMadeValues(up)+' upload', 'SpeedTest')
    lastSpeedTest = round(time.monotonic()) #Reset timer
def cc_tellrawEmoticons(user, args):
    if len(args) > 0:
        tellRaw('Click on an emoticon to copy it to your clipboard, or shift-click on it to add it to your chat', None, user)
        pageName = ' '.join(args).lower()
        tellRaw('Showing emoticon pages matching "'+pageName+'"...', None, user)
        for page in emoticons:
            if pageName in page:
                tellRaw('Emoticon page '+emoticons[page][0]+':')
                for emoticon in emoticons[page][1:]:
                    if type(emoticon) == tuple:
                        parts = ['{"text":"{%EMOTICON}","insertion":"{%EMOTICON}","clickEvent":{"action":"copy_to_clipboard","value":"{%EMOTICON}"},"hoverEvent":{"action":"show_text","contents":[{"text":"{%EMOTICON}","bold":true}]}}'.replace('{%EMOTICON}', safeTellRaw(i, False)) for i in emoticon]
                        writeCommand('tellraw '+user+' ['+('," | ",'.join(parts))+']')
                    else:
                        writeCommand('tellraw @a {"text":"{%EMOTICON}","insertion":"{%EMOTICON}","clickEvent":{"action":"copy_to_clipboard","value":"{%EMOTICON}"},"hoverEvent":{"action":"show_text","contents":[{"text":"{%EMOTICON}","bold":true}]}}'.replace('{%EMOTICON}', safeTellRaw(emoticon, False)))
    else:
        tellRaw('Click on a page name to view the contents, or use "'+chatComPrefix+'emoticons [page name]"', None, user)
        for page in emoticons:
            #writeCommand(('tellraw '+user+' [{"text":"•{%PAGE}","clickEvent":{"action":"run_command","value":"/tag @s add _rs.py_chatCommand_flag.emoticonPage.'+(page.replace(' ', '_'))+'"},"hoverEvent":{"action":"show_text","contents":[{"text":"{%PAGE}","bold":true,"underlined":true}]}}]')
            writeCommand('tellraw @p {"text":"•{%PAGE}","clickEvent":{"action":"suggest_command","value":"{%EMOTICON_COMMAND}"},"hoverEvent":{"action":"show_text","contents":[{"text":"{%PAGE}","bold":true,"underlined":true},{"text":" [{%EMOTICON_COMMAND}]","bold":false,"underlined":false}]}}'.replace('{%EMOTICON_COMMAND}', chatComPrefix+'emoticons {%PAGE}').replace('{%PAGE}', safeTellRaw(emoticons[page][0], False)))
crashParticles = ['minecraft:elder_guardian', 'minecraft:sweep_attack', 'minecraft:explosion', 'minecraft:angry_villager']
def cc_crashPlayer(user, severity=3):
    #particle <name> <pos> <delta> <speed> <count> [force|normal] [<viewers>]
    writeCommand('execute at '+user+' run particle minecraft:barrier ~ ~1.5 ~ 0 0 0 1 5 force')
    writeCommand('execute at '+user+' run particle minecraft:barrier ~ ~0.5 ~ 0 0 0 1 5 force')
    writeCommand('execute at '+user+' run particle '+random.choice(crashParticles)+' ~ ~ ~ 1 1 1 1 2147483647 force '+user)
    time.sleep(severity-1)
    for i in range(1, severity):
        writeCommand('execute at '+user+' run particle '+random.choice(crashParticles)+' ~ ~ ~ 1 1 1 1 2147483647 force '+user)
        time.sleep(i*10)
    writeCommand('kick '+user+' Timed out')

# Web interface

#  Threaded scripts

#   Initial runscript
def runWebInterfaceServer(port=8080):
    global httpd, webInterfaceAuth, keepWebIntAlive, LastRequestForWebInt
    webInterfaceAuth = keepWebIntAlive = LastRequestForWebInt = None
    httpd = http.server.ThreadingHTTPServer((ip, port), WebInterfaceServer)
    asyncTimeoutFunc(120, webInterfaceTimeout) #Starting timeout of 120 seconds
    httpd.serve_forever()

#   Timeouts
def webInterfaceTimeout():
    global keepWebIntAlive
    while True: #Checks every 40 seconds after running if "keepWebIntAlive" is true, if it isn't then it will close the server.
        if not keepWebIntAlive: break
        keepWebIntAlive = False
        time.sleep(40)
    webInterfaceAuth = None
    web_data.clear()
    print ('Web interface timed out - Stopping...')
    httpd.shutdown()
    httpd.socket.shutdown()

#  Main class
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
        logData(time.strftime('[%Y-%m-%d %H:%M:%S]')+' <GET> '+str(self.client_address)+' -> '+self.path, 'WebInterface')
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
                        writeCommand('tellraw '+webInterfaceAuthUser+' ["Your password it:\n",{"text":"'+webInterfaceAuth[0]+'","bold":true,"clickEvent":{"action":"copy_to_clipboard","value":"'+webInterfaceAuth[0]+'"},"hoverEvent":{"action":"show_text","contents":["Click to copy to clipboard"]}}]')
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
        logData(time.strftime('[%Y-%m-%d %H:%M:%S]')+' <GET> '+str(self.client_address)+' -> '+self.path, 'WebInterface')
        if int(self.headers['Content-Length']) > 500: #If the data/content/"Payload" is too big (more than 500 chars)
            self.send_response(413) #Response: 413 Payload Too Large
            self.end_headers()
            return
        data = self.rfile.read(int(self.headers['Content-Length'])).decode('UTF-8')
        if self.path == '/_send/cmd':
            data = encDec(webInterfaceAuth[0], data)
            if data:
                if not data.startswith(chatComPrefix): data = chatComPrefix+data
                if data.startswith(chatComPrefix+'root'): self.send_response(403) #Response: 403 Forbidden
                else:
                    self.send_response(200) #Response: 200 OK
                    inputQueue.append('[##:##:##] [Server thread/INFO]: <'+ccWebIUsr+'> '+data)
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

# Minecraft server handling
def startServer():
    global process #Main server process
    print ('Starting Minecraft server...')
    print (mainCommand) #"mainCommand", created earlier, is the command that is used to run the server (looks like "java -jar -Xms[ram] -Xmx[ram] [server jar dir] nogui 
    process = subprocess.Popen(mainCommand, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

# Keyboard input handler
def enterKeyPressed(key):
    try:
        line = sys.stdin.readline().rstrip() # Read a single line from sys.stdin
        if line.startswith(chatComPrefix): #It is a ChatCommand, so place it in inputQueue to be "injected" into output to prevent desync
            inputQueue.append('[##:##:##] [Server thread/INFO]: <'+ccRootUsr+'> '+line) #A queue to be ran by the "getOutput" command to synchronously perform ChatCommands from the server console
            writeCommand('') #Write this here to trigger the getOutput function to run
        else: #Otherwise pass it to the server console as normal, as the Minecraft server is asynchronous anyways
            print ('> '+line)
            writeCommand(line) #Commands can be written whenever without desync
    except:
        print ('Error when parsing input!\n'+traceback.format_exc())
def rehookKeyboard():
    print ('Unhooking keyboard...')
    keyboard.unhook_all()
    print ('Rehooking keyboard...')
    keyboard.on_press_key('enter', enterKeyPressed)
    print ('Keyboard successfully rehooked')

# Things that run on startup
def autoBackup(): #Requires Linux
    if os.name == 'nt': print ('Cannot run auto-backup on Windows')
    else:
        print ('Starting auto-backup...')
        cwd = os.getcwd()
        os.chdir(srvrFolder+'..') #Change to directory directly outside of server folder, so that the zip file has everything without a bunch of extra directory structure
        print ('zip -q -r -FS -9 '+autoBckpZip+' '+os.path.basename(cwd))
        os.system('zip -q -r -FS -9 '+autoBckpZip+' '+os.path.basename(cwd))
        os.chdir(cwd) #Go back to previous working directory to prevent conflicts
def swapIcon():
    print ('Swapping server icon...')
    if len(serverIcons) > 0:
        srvrIco = random.choice(serverIcons)
        print ('Selected server icon:\n'+os.path.basename(srvrIco)+'\nSwapping...')
        shutil.copy(srvrIco, srvrFolder+'server-icon.png') #Copy over new server icon
        print ('Done')
    else: print ('\nNO *.png SERVER ICONS PRESENT! ADD SOME IN '+iconsDir+'!\n') #If there are no server icons to choose from
def swapMOTD(uptimeStart): #MOTD = message of the day
    print ('Swapping MOTD...')
    if len(motds) > 0:
        motd = random.choice(motds)
        motd += '\\u00A7r\\n\\u00A7o(Last restart: \\u00A7n'+(time.ctime(uptimeStart).rstrip().replace('  ', ' '))+'\\u00A7r\\u00A7o)' #Add timestamp to MOTD
        print ('Selected MOTD:\n'+motd)
        if os.path.exists('server.properties'): #The properties exist
            print ('Reading properties...')
            with open('server.properties') as pf: #Read the properties
                props = pf.read().split('\n')
            print ('Adding MOTD to properties and writing back to file...')
            for i in range(len(props)): #Add the MOTD to the properties
                if props[i].startswith('motd='): props[i] = 'motd='+motd
        else: #The properties don't exist, so make a file that only includes the MOTD (the server will automatically re-create missing properties)
            print ('Properties file doesn\'t exist, making a new one...')
            props = ['server.properties']
        with open('server.properties', 'w') as pf: #Write the modified properties to the file
            pf.write('\n'.join(props))
        print ('Done')
    else: print ('\nNO MOTDs TO CHOOSE FROM! ADD SOME IN '+confDir+'motds.conf!\n') #If there are no MOTDs to choose from
def serverHandler(): #Does everything that is needed to start the server and safely close it
    global lastSpeedTest, lastTickTest, uptimeStart
    lastSpeedTest = -1
    lastTickTest = -1
    uptimeStart = time.time()
    #Setup functions
    keyboard.unhook_all() #Unhook keyboard while processes are running
    autoBackup() #Automatically backup everything
    swapIcon() #Swap the server icon (if there are any present)
    swapMOTD(uptimeStart) #Swap the server MOTD (message of the day) (if there are any present)
    makeLogFile() #Setup logging
    closeOpenFileHandles() #Close any open file handles
    #Rehook keyboard
    rehookKeyboard() #The keyboard hook is used for getting input from the server console
    #Main server starting and handling
    startServer() #Start the main server
    time.sleep(0.1) #Give it a bit of time to boot
    #Test if the EULA hasn't been written yet, and ask the user if they want to agree to it
    out = getOutput(process)
    #0         1         2         3
    #0123456789012345678901234567890
    #[13:15:14] [main/INFO]: You need to agree to the EULA in order to run the server. Go to eula.txt for more info.
    if out[0] == '[' and out[9:] == '] [main/INFO]: You need to agree to the EULA in order to run the server. Go to eula.txt for more info.':
        print ('EULA has not been agreed too')
        with open('eula.txt') as f:
            eula = f.read().split('\n')
        import webbrowser
        webbrowser.open(eula[0].split('(')[1].split(')')[0])
        del webbrowser
        if input('Do you accept the Mojang EULA? (Y/n) >').lower() == 'n': exit()
        else:
            eula[2] = 'eula=true'
            with open('eula.txt', 'w') as f:
                f.write('\n'.join(eula))
    while True: #Main loop
        try:
            getOutput(process)
        except:
            e = traceback.format_exc().rstrip()
            print ('Error caught!')
            print (e)
            try:
                for i in e.split('\n'):
                    print (safeTellRaw(i))
                    writeCommand('tellraw @a ["",{"text":'+safeTellRaw(i)+',"bold":true,"color":"red"}]')
            except:
                print (traceback.format_exc())
        if process.poll() != None: break
    #Post-server
    print ('Server closed')
    finalizeLogFile()
    keyboard.unhook_all() #Unhook keyboard
def serverLoopHandler(): #Main program that handles auto-restarting and exception catching and handling
    global restarts
    customRuntimes = {'firstStart': [], 'everyStart': [], 'lastStop': [], 'everyStop': []}
    for i in customRuntime['firstStart'](globals): i(globals)
    while True:
        try:
            for i in customRuntimes['everyStart']: i(globals)
            serverHandler()
            for i in customRuntimes['everyStop']: i(globals)
        except:
            print ('Error!\n'+traceback.format_exc())
        try:
            print (process.stdout.read().decode('UTF-8', 'replace')) #Read any leftover messages and flush buffer
        except:
            pass
        try:
            for i in range(3, 0, -1): #Countdown from 3 seconds
                print ('Auto-restarting in '+str(i)+' seconds (press CTRL+C to cancel)...')
                time.sleep(1)
            restarts += 1
        except KeyboardInterrupt:
            print ('Auto-restart cancelled')
            print ('Auto-restarted '+str(restarts)+' times')
            break
    for i in customRuntimes['lastStop']: i(globals)
    print ('Logged amount over '+str(restarts)+' restarts:\n'+str(loggedAmountTotal))

# Main
restarts = 0
serverLoopHandler()
keyboard.unhook_all()
