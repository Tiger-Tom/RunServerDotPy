#!/bin/python3

## This program is meant for Linux! Most things will probably work on Windows, but not everything. ##
## Macintoshes are also not supported ##

## This program must be run in unbuffered mode (default with "python3" command on Linux and Windows, but not IDLE) ##

# Imports

#  System
import os
import sys
import subprocess
import gc
import traceback
import threading
import platform

#  Network
import requests

#  Numbers
import time
import math

#  Files
import shutil
import zipfile

#  Etc.
import random
import json
import queue

#  Non-builtin imports
try:
    import keyboard #For the keyboard "hook", to detect enter key presses
    import psutil #Will be used to close all trailing file handles, as well as getting some system informatino
    from better_profanity import profanity #For censoring and detecting profanity in chat
except ModuleNotFoundError: #Means that we have to try to install the modules
    if input('Warning: some required modules were not found. Attempt to install? (Y/n) >').lower() == 'n': exit()
    modulesToInstall = 'keyboard psutil better_profanity pyspectator'
    print ('Installing...\npip3 -q install '+modulesToInstall)
    os.system('pip3 -q install '+modulesToInstall) #Install the modules (-q means quiet, to prevent a lot of spam in a console)
    del modulesToInstall # Free up memory, we will be seeing a lot of this
    #Try to import modules again
    import keyboard
    import psutil
    from better_profanity import profanity

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

# Fix main RunServerDotPy directory if missing
if not os.path.exists(srvrFolder+'RunServerDotPy'): os.mkdir(srvrFolder+'RunServerDotPy')

# Setup some module-related things
gc.enable()

# Setup some values
sizeVals = ['bytes', 'kibibytes', 'mebibytes', 'gibibytes', 'tebibytes']
timeVals = ['seconds', 'minutes', 'hours']

# Setup profanity filter
allowedProfaneWords = ['kill'] #Any words or phrases that should not be considered profane
allowedModifyWords = ['or41'] #Any words or phrases that may be a variation of a profane word, but should actually be allowed, as they are outputted in console
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
def runWCallback(callbackFunc, cmd): #Runs a system command and waits for it to finish, and then runs "callbackFunc" with the output as an argument
    callbackFunc(runWOutput(cmd))
def asyncRunWCallback(callbackFunc, cmd): #Runs a system command with a callback, but asynchronously
    threading.Thread(target=runWCallback, args=(callbackFunc,cmd), daemon=True).start()

#  Function functions
def funcWithDelay(delay, func, args=[], kwargs={}):
    time.sleep(delay)
    func(*args, **kwargs)

#  String formatting & similar
def makeValues(startValue, delimiter, values): #"values" is a list of strings (something like "second, minute, hour") in ascending order, "delimiter" is the divider (60 for "second, minute, hour"), and "startValue" is pretty obvious
    doneVals = {}
    previousVal = round(startValue)
    for i in range(len(values)):
        nextVal = math.floor(previousVal/delimiter)
        doneVals[values[i]] = previousVal-(nextVal*delimiter)
        previousVal = nextVal
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
def pad0s(num, padAmount=1, padOn='left', autoRound=True): #Pads the number with the specified amount of zeroes (pad0s(1, 2) = 001 , pad0s(1, 2, 'right') = 100 (useful for decimals))
    if autoRound: num = int(num+0.5) #Thanks https://stackoverflow.com/questions/44920655/python-round-too-slow-faster-way-to-reduce-precision
    if num == 0: return '0'*(padAmount+1)
    padding = ''
    while num < 10**padAmount:
        padding += '0'
        padAmount -= 1
    if padOn == 'right': return str(num)+padding
    return padding+str(num)
def getDTime(format_='%M-%D-%Y %h:%m:%s'): #Format: %M=Month;%D=Day;%Y=Year;%h=Hour;%m=Minute;%s=Second
    t = time.localtime()
    return format_.replace('%M', pad0s(t.tm_mon)).replace('%D', pad0s(t.tm_mday)).replace('%Y', str(t.tm_year)).replace('%h', pad0s(t.tm_hour)).replace('%m', pad0s(t.tm_min)).replace('%s', pad0s(t.tm_sec))

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
inputQueue = queue.Queue()
def getOutput(process): #Prints all of the process' buffered STDOUT (decoded it from UTF-8) and also returns it
    global inputQueue
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
            print ('AN ERROR OCCURED WHEN PARSING!\n'+traceback.format_exc())
    try:
        if not inputQueue.empty(): #Inject output & automatically parse it
            nxt = inputQueue.get(False, 1)
            print ('{*INJECTED} "'+nxt+'"')
            parseOutput(nxt)
    except queue.Empty:
        pass
    sys.stdout.flush()
    return data

# Get username for Ubuntu
if os.name != 'nt': bashUser = runWOutput('logname').rstrip()

# Fix cache dir (if missing)
if not os.path.exists(cacheDir): os.mkdir(cacheDir)

# Auto-update
def getVersion():
    if not os.path.exists(cacheDir+'version.txt'): currentID = -1.0
    else:
        with open(cacheDir+'version.txt') as f:
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
    with open(cacheDir+'version.txt', 'w') as f:
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
ccRootUsr = '§server admin__'
confFiles = { #'[name].conf': '[default contents]',
    'admins.conf': ccRootUsr,
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
logFiles = ['Chat', 'RawChat', 'ChatCommands', 'Profanity', 'Unusual+Errors']
loggedAmountTotal = {} #Total amount of logs collected
loggedAmountIter = {} #Amount of logs collected since last finalized log
logFileHandles = {}

#  Logging functions
def makeLogFile(): #Setup the log file
    global logStartTime
    t = time.localtime()
    if not os.path.exists(logDir): os.mkdir(logDir) #Fix logging directory if it doesn't exist
    logStartTime = getDTime('%M;%D;%Y;%h;%m').split(';')
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
    if lost: targetDir = logDir+'Lost/FOUND_ON_'+getDTime('%M-%D-%Y_%h-%m-%s')+'.zip'
    else:
        curTime = getDTime('%M;%D;%Y;%h;%m').split(';')
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
        lfHandle.write(getDTime('[%M-%D-%Y %h:%m:%s] ')+data.rstrip()+'\n')
    except (ValueError, KeyError): #File handle never made or does not exist #Make sure not to catch the wrong exceptions
        if not os.path.exists(logDir+'latest/'): os.mkdir(logDir+'latest/')
        lfHandle = open(logDir+'latest/'+category+'.txt', 'a+', encoding='UTF-16')
        logFileHandles[category] = lfHandle
        lfHandle.write(getDTime('>>[NEW HANDLE OPENED]<<\n[%M-%D-%Y %h:%m:%s] ')+data.rstrip()+'\n')
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
def safeTellRaw(text): return json.dumps(text.rstrip()) #Formats a string to be safe for use in a tellraw command
def tellRaw(text, frmTxt=None, to='@a'): #Runs the tellraw commands, and adds a "from" text if frmTxt is not None (with a from text would look like: <"frmTxt"> "text")
    if (to == ccRootUsr) or (ccRootUsr in str(frmTxt)) or (ccRootUsr in text):
        if frmTxt != None: print (frmTxt+' > "'+text+'"')
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
def parseOutput(line): #Parses the output, running subfunctions for logging and parsing chat
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
            elif chatL[0] == 3: logData('"'+chatL[1]+'" /said "'+chatL[2]+'"', 'Chat') #Is a /say message, save it in the chat log formatted like: "[User]" /said "[Message]"
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
    rewriteHelp = False
    if not os.path.exists(cacheDir+'help/'): os.mkdir(cacheDir+'help/') #Create help cache directory if it doesn't exist
    if not os.path.exists(cacheDir+'help/version.txt'): #Create help version file if it doesn't exist
        with open(cacheDir+'help/version.txt', 'w') as f:
            rewriteHelp = True
    if not rewriteHelp: #Compare current help version with newest help version
        with open(cacheDir+'help/version.txt') as f:
            newVer = getFileFromServer('https://raw.githubusercontent.com/Tiger-Tom/RunServerDotPy-extras/main/Help/Version').rstrip().split('/')
            curVer = f.read().rstrip().split('/')[1]
            print ('Current help version: '+str(getVersion())+'/'+str(curVer)+'\nNewest help version: '+('/'.join(newVer)))
            if getVersion() < float(newVer[0]):
                rewriteHelp = False
                print ('Did not update help file, as current program version is outdated anyways')
            elif float(curVer) < float(newVer[1]):
                rewriteHelp = True
                print ('Help file needs updating, current version is out of date')
    if rewriteHelp: #Update cached help JSON to latest version
        with open(cacheDir+'help/ChatCommandsHelp.json', 'w') as f:
            f.write(getFileFromServer('https://raw.githubusercontent.com/Tiger-Tom/RunServerDotPy-extras/main/Help/ChatCommandsHelp.json'))
        with open(cacheDir+'help/version.txt', 'w') as f:
            f.write(getFileFromServer('https://raw.githubusercontent.com/Tiger-Tom/RunServerDotPy-extras/main/Help/Version'))
    with open(cacheDir+'help/ChatCommandsHelp.json') as f:
        chatCommandsHelp,chatCommandsHelpAdmin,chatCommandsHelpRoot = json.load(f) #Load ChatCommands help from cached JSON file
#    Remove unusable help strings
    if os.name == 'nt': del chatCommandsHelpAdmin['update | upgrade {dist,clean,pip}'] #The necessary commands to update/upgrade are not on Windows, so delete the help string

#   Configuration variables
sysInfoShown = {
    'cpu': True,
    'memory': True,
    'temp': True,
    'battery': True,
    'diskrw': True,
}
if not hasattr(psutil, 'sensors_battery'): sysInfoShown['battery'] = False #Don't show battery level, as it can't be read
if not hasattr(psutil, 'sensors_temperatures'): sysInfoShown['temp'] = False #Don't show temperature, as it can't be read

#  Functions
def parseChatCommand(user, data):
    data = data.split(' ')
    cmd = data[0][1:].lower()
    args = data[1:]
    if cmd in {'root', 'sudo'}: #The command is not a normal-level command (a {} is a set, which saves time for something like this because it is unordered and unindexed)
        print (user+' is trying to run '+cmd+'-level ChatCommand "'+args[0]+'" with '+str(len(args[1:]))+' arguments')
        comm = args[0].lower()
        args = args[1:]
        if cmd == 'root': #The command is a root-level command (only server console can run)
            if user == ccRootUsr: #User has permissions, run command
                print ('Root access granted, '+user)
                runRootChatCommand(comm, args)
            else: #User does not have permissions, kick them from the server
                tellRaw('Root access denied, '+user+'. You do not have access level "root"!', 'Firewall')
                writeCommand('kick '+user+' Root access denied, '+user+'. You do not have access level "root"!')
        else: #Administrator command, 
            if user in admins:
                tellRaw('SuperUser access granted, '+user, 'Firewall')
                runAdminChatCommand(comm, args, user)
            else:
                tellRaw('SuperUser access denied, '+user+'. You do not have access level "admin"!', 'Firewall')
                writeCommand('kick '+user+' SuperUser access denied, '+user+'. You do not have access level "admin"!')
    else:
        print (user+' is attempting to run ChatCommand "'+cmd+'" with '+str(len(args))+' arguments')
        chatCommandsLastUsed.setdefault(user, 0)
        if time.monotonic()-chatCommandsLastUsed[user] < 1: writeCommand('kick '+user+' SpamProtection: Please wait 1 second between ChatCommands')
        else: runChatCommand(cmd, args, user)
        if not user in admins: chatCommandsLastUsed[user] = time.monotonic() #User is not an admin, so reset their timer

#   ChatCommand subfunctions
def cc_help(ccHelpDict, args, ccPref=chatComPrefix, user='', toConsole=False): #If "toConsole" is True, then this just prints it. Otherwise, it uses a tellraw command
    if user == ccRootUsr: toConsole = True
    if not len(args): command = None
    else: command = ' '.join(args)
    if command == None: cHelp = 'List of commands:\n("command" | "variation" ["positional arg(s) *=optional"] {"flags"}\n(Command prefix: '+ccPref+')\n(Use '+ccPref+'help [command] for help on a specific command)'
    else: cHelp = 'Help page for commands matching "'+command+'":'
    if toConsole: print (cHelp)
    else: tellRaw(cHelp, 'Help', user)
    showAll = (command == None) #Save a bit of time from calculations
    for i in ccHelpDict.keys():
        if showAll:
            if toConsole: print (' • '+i)
            else: writeCommand('tellraw '+user+(' [" • ",{"text":"{%COMMAND_FULL}","clickEvent":{"action":"suggest_command","value":"{%COMMAND_SUGGEST}"},"hoverEvent":{"action":"show_text","contents":[{"text":"{%COMMAND_SUGGEST}","bold":true}]}}]').replace('{%COMMAND_FULL}', i).replace('{%COMMAND_SUGGEST}', ccPref+i.split(' ')[0]))
        else:
            if command in i:
                if toConsole: print (' • '+i+': '+ccHelpDict[i])
                else: writeCommand('tellraw '+user+(' [" • ",{"text":"{%COMMAND_FULL}","clickEvent":{"action":"suggest_command","value":"{%COMMAND_SUGGEST}"},"hoverEvent":{"action":"show_text","contents":[{"text":"{%COMMAND_SUGGEST}","bold":true}]}},{"text":": {%COMMAND_DESC}","hoverEvent":{"action":"show_text","contents":[{"text":"{%COMMAND_DESC}","bold":true}]}}]').replace('{%COMMAND_FULL}', i).replace('{%COMMAND_SUGGEST}', ccPref+i.split(' ')[0]).replace('{%COMMAND_DESC}', ccHelpDict[i]))
def cc_parseSpeedTest(res):
    res = json.loads(res)
    down = makeValues(res['download'], 1024, sizeVals)
    up = makeValues(res['upload'], 1024, sizeVals)
    tellRaw(parseMadeValues(down)+' download', 'SpeedTest')
    tellRaw(parseMadeValues(up)+' upload', 'SpeedTest')
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
                        parts = ['{"text":"{%EMOTICON}","insertion":"{%EMOTICON}","clickEvent":{"action":"copy_to_clipboard","value":"{%EMOTICON}"},"hoverEvent":{"action":"show_text","contents":[{"text":"{%EMOTICON}","bold":true}]}}'.replace('{%EMOTICON}', i) for i in emoticon]
                        writeCommand('tellraw '+user+' ['+('," | ",'.join(parts))+']')
                    else:
                        writeCommand('tellraw @a {"text":"{%EMOTICON}","insertion":"{%EMOTICON}","clickEvent":{"action":"copy_to_clipboard","value":"{%EMOTICON}"},"hoverEvent":{"action":"show_text","contents":[{"text":"{%EMOTICON}","bold":true}]}}'.replace('{%EMOTICON}', emoticon))
    else:
        tellRaw('Click on a page name to view the contents, or use "'+chatComPrefix+'emoticons [page name]"', None, user)
        for page in emoticons:
            writeCommand(('tellraw '+user+' [{"text":"•{%PAGE}","clickEvent":{"action":"run_command","value":"/tag @s add _rs.py_chatCommand_flag.emoticonPage.'+(page.replace(' ', '_'))+'"},"hoverEvent":{"action":"show_text","contents":[{"text":"{%PAGE}","bold":true,"underlined":true}]}}]').replace('{%PAGE}', emoticons[page][0]))
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
def cc_parseTagFlag(flag, user):
    # tag [user] add _rs.py_chatCommand_flag.[flag]
    print ('% "'+user+'" triggered flag "'+flag+'"')
    writeCommand('tag '+user+' remove _rs.py_chatCommand_flag.'+flag)
    flag = flag.split('.')
    if flag[0] == 'emoticonPage':
        threading.Thread(target=cc_tellrawEmoticons, args=(user,('.'.join(flag[1:])).split('_')), daemon=True).start()
    else:
        print ('% ERROR: UNKNOWN FLAG "'+str(flag)+'"')

#   Basic functions (any user can run)
def runChatCommand(cmd, args, user):
    tellRaw('Running ChatCommand '+cmd, '$ '+user)
    if cmd == 'help': cc_help(chatCommandsHelp, args, user=user) #Displays a list of commands, or details for a specific command if it is specified in the arguments
    elif (cmd == 'emoticons') and (user != ccRootUsr): threading.Thread(target=cc_tellrawEmoticons, args=(user,args), daemon=True).start() #Shows a list of copyable emoticons, which are configurable by the server owner
    elif (cmd == 'nuke') and (user != ccRootUsr): cc_crashPlayer(user, 1) #Secret command
    elif cmd == 'size': #Displays the size of the server's world folder
        size = 0
        for path, dirs, files in os.walk(srvrFolder+'world/'):
            for f in files:
                size += os.path.getsize(os.path.join(path, f))
        for i in os.scandir(srvrFolder):
            size += os.path.getsize(i)
        tellRaw('The server world folder is '+parseMadeValues(makeValues(size, 1024, sizeVals))+' large', 'Size', user)
    elif cmd == 'speedtest': #Runs an internet speed test
        global lastSpeedTest
        waitSecs = 600
        timeSinceLast = round(time.monotonic())-lastSpeedTest
        if (timeSinceLast > waitSecs) or (user in admins): #Enough time has passed since last ran, or the user is an admin
            lastSpeedTest = round(time.monotonic()) #Reset timer
            tellRaw('Beginning asynchronous speed test...\nThis could take a little while', 'SpeedTest')
            asyncRunWCallback(cc_parseSpeedTest, 'speedtest-cli --json')
        else:
            print ('Last speed test: '+str(lastSpeedTest))
            tellRaw('Please wait '+parseMadeValues(makeValues(600-timeSinceLast, 60, timeVals))+' to run another speed test', 'SpeedTest')
    elif cmd in {'sysinfo', 'info'}:
        tellRaw('System information for '+platform.node()+':', 'SysInf', user)
        if sysInfoShown['cpu']: tellRaw(str(psutil.cpu_percent())+'% of CPU used', None, user)
        if sysInfoShown['memory']: tellRaw(str(psutil.virtual_memory().percent)+'% of memory used', None, user)
        if sysInfoShown['temp']:
            temps = psutil.sensors_temperatures()
            for i in temps:
                t = 0
                for j in temps[i]:
                    t += j.current
                t = t/len(temps[i])
                if tempUnit[0] == 2: t += 273.15 #Convert to kelvin if needed
                elif tempUnit[0] == 1: t = (t*(9/5))+32 #Convert to Fahrenheit if needed
                tellRaw('Temperature "'+i+'" is '+str(t)+tempUnit[1], None, user)
        if sysInfoShown['battery']: tellRaw('Battery has '+str(psutil.sensors_battery().percent)+'% charge (Plugged in: '+('yes' if psutil.sensors_battery().power_plugged else 'no')+')', None, user)
        if sysInfoShown['diskrw']:
            ioCount = psutil.disk_io_counters()
            tellRaw('The disk has had a total of '+parseMadeValues(makeValues(ioCount.read_bytes, 1024, sizeVals))+' reads and '+parseMadeValues(makeValues(ioCount.write_bytes, 1024, sizeVals))+' writes since the last system restart')
    elif cmd == 'tps': #Gets the server's TPS over a 10 second period
        #*10:          1         2         3         4         5         6
        #*1 :0123456789012345678901234567890123456789012345678901234567890123456789
        #    [14:47:22] [Server thread/INFO]: Stopped tick profiling after 10.81 seconds and 217 ticks (20.08 ticks per second)
        #           9:                                       :48         62:0     1       2   3   4     5     6     7   8
        global lastTickTest
        waitSecs = 120
        timeSinceLast = round(time.monotonic())-lastTickTest
        if (timeSinceLast > waitSecs) or (user in admins): #Enough time has passed since last ran, or the user is an admin
            lastTickTest = round(time.monotonic()) #Reset timer
            tellRaw('Beginning asynchronous TPS test...\nThis should take about 10 seconds', 'TPSTest')
            writeCommand('debug start')
            threading.Thread(target=funcWithDelay, args=(10, writeCommand, ['debug stop']), daemon=True).start()
            while True:
                out = getOutput(process)
                if (out[0] == '[') and (out[9:48] == '] [Server thread/INFO]: Stopped tick pr'):
                    out = out[62:].split(' ')
                    break
            secsTest = out[0]
            ticksTest = out[3]
            tpsTest = out[5][1:]
            tellRaw('Test lasted '+secsTest+' seconds ('+ticksTest+' ticks)\nRunning at about '+tpsTest+' ticks per second (should be ~20)', 'TPSTest')
    elif cmd == 'uptime': #Gets the server and system's uptime
        tellRaw('The server has been online for '+parseMadeValues(makeValues(round(time.monotonic()-uptimeStart), 60, timeVals)), 'Uptime', user)
        tellRaw('(Online since '+(time.ctime(uptimeStart).rstrip().replace('  ', ' '))+')', None, user)
        tellRaw('The system has been powered on for '+parseMadeValues(makeValues(round(time.monotonic()-psutil.boot_time()), 60, timeVals)), 'Uptime', user)
        tellRaw('(Powered on since '+(time.ctime(psutil.boot_time()).rstrip().replace('  ', ' '))+')', None, user)
    else: tellRaw('Unknown command "'+cmd+'", sorry', 'CCmd', user)

#   Sudo/admin commands (only admins or server console can run these commands)
def runAdminChatCommand(cmd, args, user):
    tellRaw('Running SuperUser ChatCommand '+cmd, '$'+user, user)
    if cmd == 'help': cc_help(chatCommandsHelpAdmin, args, chatComPrefix+'sudo', user) #Display a list of admin commands, or information on a specific one if specified in arguments
    elif cmd in {'antimalware', 'antivirus', 'scan'}:
        tellRaw('Operating system: '+os.name, 'AntiMal')
        if os.name == 'nt':
            tellRaw('Scanner: Windows Defender', 'AntiMal')
            comm = '"%ProgramFiles%/Windows Defender/MpCmdRun.exe" -Scan'
        else:
            tellRaw('Scanner: ClamAV', 'AntiMal')
            if shutil.which('clamscan') == None: #ClamAV is not installed, so install it
                comm = 'sudo apt-get install clamav libfreshclam'
                tellRaw(comm)
                runWFullOutput(comm, tellRaw)
                os.system('sudo systemctl stop clamav-freshclam.service')
                os.system('sudo systemctl disable clamav-freshclam.service')
            comm = 'sudo freshclam'
            tellRaw(comm)
            runWFullOutput(comm, tellRaw)
            comm = 'sudo clamscan --quiet -r /'
        tellRaw(comm)
        asyncRunWCallback(tellRaw, comm)
        tellRaw('This will last a while. The results will be displayed once the scan is complete', 'AntiMal')
    elif cmd == 'ban': #Bans a user for (optional) reason. Uses the in-game /ban command
        if len(args) > 1: tellRaw('Banning '+args[0]+' for '+(' '.join(args[1:])), 'Ban', user)
        else: tellRaw('Banning '+args[0], 'Ban', user)
        writeCommand('ban '+(' '.join(args)))
        if len(args) > 1: tellRaw(args[0]+' was banned for '+(' '.join(args[1:]))+' by '+user, 'Ban')
        else: tellRaw(args[0]+' was banned by '+user, 'Ban')
    elif cmd == 'crash':
        target = args[0]
        if len(args) > 1:
            severity = int(args[1])
            if severity < 1 or severity > 5:
                tellRaw('Severity cannot be more than 5 or less than 1', 'Crasher', user)
                return
        else: severity = 3
        tellRaw('Crashing player '+target+' with severity '+str(severity), 'Crasher', user)
        threading.Thread(target=cc_crashPlayer, args=(target,severity), daemon=True).start()
        'crash [player] [severity*=3, 1-5]'
    elif cmd == 'kick': #Kicks a user for (optional) reason. Uses the in-game /kick command
        if len(args) > 1: tellRaw('Kicking '+args[0]+' for '+(' '.join(args[1:])), 'Kick', user)
        else: tellRaw('Kicking '+args[0], 'Ban', user)
        writeCommand('kick '+(' '.join(args)))
    elif cmd == 'logs': #Displays how many logs have been collected
        if 'total' in args: tellRaw('Logged amount over '+str(restarts)+' restarts:\n'+str(loggedAmountTotal), 'Logs', user)
        else: tellRaw('Logged amount for this iteration:\n'+str(loggedAmountIter), 'Logs', user)
    elif cmd == 'reconfig': #Reloads RunServerDotPy's configuration
        tellRaw('Reloading configuration...', 'Config', user)
        loadConfiguration()
        tellRaw('Done', 'Config', user)
    elif cmd == 'refresh': #Restarts RunServerDotPy, implementing any changes that have occured in the code
        tellRaw('Refreshing server...', user)
        runAdminChatCommand('stop', [], user) #Manually calls the "stop" admin ChatCommand with the user as the executor
        print ('Unhooking keyboard...')
        keyboard.unhook_all()
        while process.poll() == None: #Get remaining output while the process is still running
            getOutput(process)
        try:
            process.wait() #Wait for the process to complete
            print (process.stdout.read().decode('UTF-8', 'replace')) #Read any leftover messsages and flush buffer
        except:
            pass
        finalizeLogFile() #Finalize the log file
        closeOpenFileHandles() #Important, because command below leaves file handles open
        print ('Goodbye')
        os.execl(sys.executable, sys.executable, *sys.argv) #Immediately replace the current process with this one, retaining arguments
    elif cmd == 'reload': #Reloads the server's resources, using the in-game /reload command
        tellRaw('Reloading!', None, user)
        writeCommand('reload')
    elif cmd in {'restart', 'stop'}: #Stops the server, using the in-game /stop command
        tellRaw('Restarting server...', user)
        for i in range(3, 1, -1): #Countdown to warn users
            writeCommand('tellraw @a {"text":"Warning! Server closing for a restart in '+str(i)+' seconds!","bold":true,"color":"red"}')
            time.sleep(1)
        writeCommand('tellraw @a {"text":"Warning! Server closing for a restart in 1 second!","bold":true,"color":"red"}')
        time.sleep(1)
        writeCommand('tellraw @a ["",{"text":"Warning! Server closing for a restart ","bold":true,"color":"red"},{"text":"NOW!","bold":true,"color":"dark_red"}]')
        writeCommand('kick @a Server restarting!') #Kick all the players from the server
        writeCommand('save-all') #Save the game
        writeCommand('stop') #Stop the server
    elif cmd in {'save', 'save-all'}: #Saves the game, using the in-game /save-all command
        tellRaw('Saving the game')
        writeCommand('save-all')
        tellRaw('Saved the game')
    elif cmd in {'unban', 'pardon'}: #Unbans a user, using the in-game /pardon command
        tellRaw('Unbanning '+(' '.join(args[0])), 'Pardon', user)
        writeCommand('pardon '+(' '.join(args)))
    elif (os.name != 'nt') and (cmd in {'update', 'upgrade'}): #Updates system packages, and optionally distribution and pip, and optionally auto-cleans. Linux only
        tellRaw('Updating package lists...', 'Update')
        cmd = 'sudo apt-get update'
        tellRaw(cmd)
        runWFullOutput(cmd, tellRaw)
        tellRaw('Done', 'Update')
        tellRaw('Upgrading packages...', 'Upgrade')
        cmd = 'yes | sudo apt-get upgrade'
        tellRaw(cmd)
        runWFullOutput(cmd, tellRaw)
        tellRaw('Done', 'Upgrade')
        if 'dist' in args:
            tellRaw('Running distribution upgrade...', 'DistUpgr')
            cmd = 'yes | sudo apt-get dist-upgrade'
            tellRaw(cmd)
            runWFullOutput(cmd, tellRaw)
            tellRaw('Done', 'DistUpgr')
        if 'clean' in args:
            tellRaw('Auto-cleaning packages...', 'AutoClean')
            cmd = 'yes | sudo apt-get autoclean'
            tellRaw(cmd)
            runWFullOutput(cmd, tellRaw)
            cmd = 'yes | sudo apt-get autoremove'
            tellRaw(cmd)
            runWFullOutput(cmd, tellRaw)
            tellRaw('Done', 'AutoClean')
        del cmd
    else: tellRaw('Unknown command "'+cmd+'", sorry', 'OPCCmd', user)

#   Root commands (only server console can run these commands)
def runRootChatCommand(cmd, args):
    print ('$ Running Root ChatCommand '+cmd)
    if cmd == 'help': cc_help(chatCommandsHelpRoot, args, chatComPrefix+'root', '', True)
    elif cmd == 'clearlogs':
        global loggedAmountIter, loggedAmountTotal
        print ('Finishing logs so that they can be safely removed...')
        finalizeLogFile()
        print ('Removing log directory...')
        shutil.rmtree(logDir)
        loggedAmountIter = {}
        loggedAmountTotal = {}
        print ('Removed logs')
        print ('Running startup for new logs...')
        makeLogFile()
        print ('All logs have been deleted')
    elif cmd == 'py':
        com = ' '.join(args)
        print ('> "'+com+'" > Python')
        print ('< "'+str(eval(com))+'"')
    else: print ('Unknown command "'+cmd+'" (args: '+str(args)+')')

# Indev AntiCheat (not currently in development)
def getPlayerPos(user):
    #Index: 0123456789012345678901234567890123456789
    #Chat:  [HH:MM:SS] [Server thread/INFO]: <Username> Message
    #/me:   [HH:MM:SS] [Server thread/INFO]: * Username Message
    #Death: [HH:MM:SS] [Server thread/INFO]: Username was slain by Entity Name
    writeCommand('data get entity '+user+' Pos')
    while True:
        out = getOutput(process)
        if out[0] == '[' and out[9] == ']' and out[11:33] == '[Server thread/INFO]: ':
            out = out[33:]
            if out.lower().startswith(user.lower()+' has the following entity data: '):
                pos = out.split('[')[1].split(']')[0].replace('d', '').split(', ')
                break
    for i in range(len(pos)):
        pos[i] = round(float(pos[i]))
    return pos

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
            inputQueue.put('[##:##:##] [Server thread/INFO]: <'+ccRootUsr+'> '+line, False) #A queue to be ran by the "getOutput" command to synchronously perform ChatCommands from the server console
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
    uptimeStart = time.monotonic()
    #Setup functions
    keyboard.unhook_all() #Unhook keyboard while processes are running
    autoBackup() #Automatically backup everything
    updateHelp() #Update the help cache file
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
    while True:
        try:
            serverHandler()
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
        except KeyboardInterrupt:
            print ('Auto-restart cancelled')
            print ('Auto-restarted '+str(restarts)+' times')
            break
    print ('Logged amount over '+str(restarts)+' restarts:\n'+str(loggedAmountTotal))

# Main
restarts = 0
serverLoopHandler()
keyboard.unhook_all()
