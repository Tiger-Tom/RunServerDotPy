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
    if input('Warning: some required modules were not found. Attempt to install? (Y/n) >').lower() == 'n':
        exit()
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
    if input('Speedtest is not installed ("speedtest-cli"). Attempt to install? (Y/n) >').lower() == 'n':
        exit()
    if os.name != 'nt': #For Linux
        os.system('yes | apt-get install speedtest-cli')
    else:
        os.system('pip3 -q install speedtest-cli') #Fallback to install with PIP

# Directories
#All directories should be followed by a "/"
baseDir = os.path.split(os.getcwd())[0] # ../
srvrFolder = os.getcwd()+'/' # ./
confDir = srvrFolder+'RunServerDotPy/Config/' # ./RunServerDotPy/Config/
iconsDir = confDir+'Icons/' # ./RunServer/Config/Icons/
autoBckpZip = baseDir+'server-backup/main_backup.zip' # ../server-backup/main_backup.zip
logDir = srvrFolder+'RunServerDotPy/Logs/' # ./RunServerDotPy/Logs/
totalLogDir = logDir+'Total/' # ./RunServerDotPy/Logs/Total/

# Fix main RunServerDotPy directory if missing
if not os.path.exists(srvrFolder+'RunServerDotPy'):
    os.mkdir(srvrFolder+'RunServerDotPy')

# Setup some module-related things
gc.enable()

# Setup some values
sizeVals = ['bytes', 'kibibytes', 'mebibytes', 'gibibytes', 'tebibytes']
timeVals = ['seconds', 'minutes', 'hours']

# Setup profanity filter
allowedProfaneWords = ['kill'] #Any words or phrases that should not be considered profane
allowedModifyWords = ['or41'] #Any words or phrases that may be a variation of a profane word, but should actually be allowed
profanity.load_censor_words(whitelist_words=allowedProfaneWords) #whitelist_words - Whitelist some words ("kill" shows up in game, for instance, but is not a swear)
for i in allowedModifyWords:
    if i in profanity.CENSOR_WORDSET:
        del profanity.CENSOR_WORDSET[profanity.CENSOR_WORDSET.index(i)]

# Base simple functions

#  System commands
def runWOutput(cmd): #Runs a system command and returns the output
    out = subprocess.check_output(cmd, shell=True)
    if type(out) == bytes: #Automatically decode it from UTF-8
        return out.decode('UTF-8')
    return out
def runWFullOutput(cmd, callbackFunc, callbackFuncXtraArgs=[]): #Runs a system command, and runns the callback function with each output
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    while True:
        out = proc.stdout.readline().decode('UTF-8')
        if not len(out):
            break
        callbackFunc(out, *callbackFuncXtraArgs)
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
            if i.endswith('s') and (values[i] == 1):
                newVals[i[:-1]] = str(values[i]) #Set "newVals" to "values" with index "i", but remove the last character of the key when saving to "newVals" (removes the trailing "s" to make it singular)
            else:
                newVals[i] = str(values[i])
    if len(newVals) == 0:
        newVals = {tuple(values)[0]: str(tuple(values.values())[0])}
    if len(newVals) == 1:
        return tuple(newVals.values())[0]+' '+tuple(newVals)[0]
    elif len(newVals) == 2:
        indx = 0
        if doReverse:
            indx = 1
        return tuple(newVals.values())[indx]+' '+tuple(newVals)[indx]+' and '+tuple(newVals.values())[1-indx]+' '+tuple(newVals)[1-indx]
    else:
        print (newVals)
        res = ''
        keys = list(newVals)
        if doReverse:
            keys.reverse()
        for i in keys[:-1]:
            res += newVals[i]+' '+i+', '
        return res+'and '+newVals[keys[-1]]+' '+keys[-1]
def pad0s(num, padAmount=1, padOn='left', autoRound=True): #Pads the number with the specified amount of zeroes (pad0s(1, 2) = 001 , pad0s(1, 2, 'right') = 100 (useful for decimals))
    if autoRound:
        num = round(num)
    if num == 0:
        return '0'*(padAmount+1)
    padding = ''
    while num < 10**padAmount:
        padding += '0'
        padAmount -= 1
    if padOn == 'right':
        return str(num)+padding
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
    zf = zipfile.ZipFile(zipPath, openMode, zipfile.ZIP_DEFLATED, compresslevel=compressionLevel)
    for root, dirs, files in os.walk(dirPath):
        for file in files:
            zf.write(root+'/'+file, os.path.relpath(root+'/'+file, dirPath))
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

#  Subprocess functions
inputQueue = queue.Queue()
def getOutput(process): #Prints all of the process' buffered STDOUT (decoded it from UTF-8) and also returns it
    global inputQueue
    try:
        data = process.stdout.readline().decode('UTF-8').rstrip()
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
        print ('Empty queue!')
    sys.stdout.flush()
    return data

# Get username for Ubuntu
if os.name != 'nt': #Not Windows
    bashUser = runWOutput('logname').rstrip()

# Configuration

#  Set custom user join message
userJoinMSG = '{"text":"Welcome, {%USER}!","clickEvent":{"action":"copy_to_clipboard","value":"{%USER}"},"hoverEvent":{"action":"show_text","contents":[{"text":"Click here to copy username to clipboard","italic":true}]}}'

#  Set config defaults
if not os.path.exists(confDir):
    os.mkdir(confDir)
ccRootUsr = '§server admin__'
emoticonsReq = requests.get('https://raw.githubusercontent.com/Tiger-Tom/RunServerDotPy-extras/main/Default%20Emoticon%20Configuration')
print (emoticonsReq.encoding)
confFiles = { #'[name].conf': '[default contents]',
    'admins.conf': ccRootUsr,
    'motds.conf': 'Minecraft Server (Version {%VERSION})',
    'serverVersion.conf': 'Configure this in serverVersion.conf!',
    'ramInMB.conf': '1024',
    'chatCommandPrefix.conf': ';',
    'tempUnit.conf': 'c',
    'emoticons.conf': emoticonsReq.text,
}
for i in confFiles:
    if not os.path.exists(confDir+i):
        with open(confDir+i, 'w', encoding='UTF-16') as cf:
            cf.write(confFiles[i]) #Write defaults if missing
        
#  Read configs
def loadConfiguration():
    print ('Loading configuration...')
    global admins, srvrVersionTxt, motds, ramMB, chatComPrefix, tempUnit, emoticons
    with open(confDir+'admins.conf') as f:
        admins = set(f.read().split('\n')) #Usernames of server administrators, who can run "sudo" commands (in a set, since it is faster because sets are unindexed and unordered)
    with open(confDir+'serverVersion.conf') as f:
        srvrVersionTxt = f.read().rstrip()
    with open(confDir+'motds.conf') as f:
        motds = f.read().rstrip().replace('{%VERSION}', srvrVersionTxt).split('\n') #List of MOTDs (single line only, changes every server restart)
    with open(confDir+'ramInMB.conf') as f:
        ramMB = int(f.read().rstrip())
    with open(confDir+'chatCommandPrefix.conf') as f:
        chatComPrefix = f.read().rstrip()
    with open(confDir+'tempUnit.conf') as f:
        tempUnit = f.read().lower()
        if tempUnit == 'c':
            tempUnit = [0, '°C']
        elif tempUnit == 'f':
            tempUnit = [1, '°F']
        elif tempUnit == 'k':
            tempUnit = [1, 'K']
        else:
            raise Exception('Unknown temperature unit "'+tempUnit+'"! Must be "c"|"f"|"k"!')
    with open(confDir+'emoticons.conf', encoding='UTF-16') as f:
        e = f.read().rstrip().split('\n')
        emoticonLines = []
        emoticonSingles = []
        emoticonDelay = float(e[0])
        e = e[1:]
        for i in e:
            if (len(i) == 0) or i.startswith('#'):
                pass
            elif i.startswith('&'):
                emoticonSingles.append(i[1:])
            else:
                emoticonLines.append(i)
        emoticons = [emoticonDelay, emoticonLines, emoticonSingles]
    print ('Configuration loaded')
loadConfiguration()

#  Display configuration
print ('Administrators:\n'+(', '.join(admins)))
print ('Server version text: "'+srvrVersionTxt+'"')
print ('Allocated server RAM: '+str(ramMB)+' MB')
print ('ChatCommand prefix: "'+chatComPrefix+'"')

#  Load icons
#(icons change every server restart, and must be 64*64 pixel PNGs. They can be named anything)
if not os.path.exists(iconsDir): #Fix if missing
    os.mkdir(iconsDir)
serverIcons = []
for i,j,k in os.walk(iconsDir): #Find all *.png's in the icon directory
    for l in k:
        if k.endswith('.png'):
            print (i+l)
            serverIcons.append(i+l)
        else:
            print ('Warning: a non-png file is in the icons directory:\n'+i+l)
print ('Server MOTDs:\n'+(', '.join(motds)))

# Command generation
mainCommand = 'java -jar -Xms'+str(ramMB)+'M -Xmx'+str(ramMB)+'M "'+srvrFolder+'server.jar" nogui'

# Logging
logFiles = ['Chat', 'RawChat', 'Profanity', 'Unusual+Errors']
loggedAmountTotal = {} #Total amount of logs collected
loggedAmountIter = {} #Amount of logs collected since last finalized log
logFileHandles = {}

#  Logging functions
def makeLogFile(): #Setup the log file
    global logStartTime
    t = time.localtime()
    if not os.path.exists(logDir): #Fix logging directory if it doesn't exist
        os.mkdir(logDir)
    #currentLogDir = logDir+getDTime('%M-%D-%Y_%h-%m')+'--{\\NEXT_TIME/}.zip'
    logStartTime = getDTime('%M;%D;%Y;%h;%m').split(';')
    if not os.path.exists(logDir+'latest/'):
        os.mkdir(logDir+'latest/')
def finalizeLogFile(lost=False): #Finish the log file and save it
    global loggedAmountIter
    global logFileHandles
    #Repair missing dirs
    if not os.path.exists(totalLogDir):
        os.mkdir(totalLogDir)
    if lost and not os.path.exists(logDir+'Lost/'):
        os.mkdir(logDir+'Lost/')
    #Close open log file handles
    for i in logFileHandles.keys():
        print ('Closing log file handle for "'+i+'"...')
        try:
            logFileHandles[i].close()
        except:
            print ('Could not close log file handle for "'+i+'" because\n'+traceback.format_exc())
    #Make file name
    if lost:
        targetDir = logDir+'Lost/FOUND_ON_'+getDTime('%M-%D-%Y_%h-%m-%s')+'.zip'
    else:
        curTime = getDTime('%M;%D;%Y;%h;%m').split(';')
        targetDir = logDir+('-'.join(logStartTime[0:3]))+'_'+('-'.join(logStartTime[3:]))+'__'
        if logStartTime[2] == curTime[2]: #Year is the same, so delete it
            indx = 2
        else:
            indx = 3
        targetDir += '-'.join(curTime[0:indx])+'_'+('-'.join(curTime[indx:]))+'.zip'
    #Don't save something if nothing is logged
    if (loggedAmountIter == {}) and not lost:
        print ('Not saving log file, as there is nothing to save!')
        return False
    if lost:
        print ('Saving lost log...')
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
        lfHandle = open(logDir+'latest/'+category+'.txt', 'a+')
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

#  Fix "lost" log if it exists
if os.path.exists(logDir+'latest/'):
    finalizeLogFile(True)

#  Initialize log file
makeLogFile()

# Minecraft server utilities

#  Commands
def writeCommand(cmd): #Writes "cmd" to the process' STDIN and adds '\n' to make it run, while also encoding it in UTF-8
    try:
        if process.poll() == None:
            process.stdin.write((cmd+'\n').encode('UTF-8'))
            process.stdin.flush()
        else:
            raise NameError
    except NameError:
        print ('Cannot write command, as process has been stopped')
#   Tellraw
def safeTellRaw(text): #Formats a string to be safe for use in a tellraw command. Escapes \, ', ", etc.
    toEscape = ['\\', '\'', '"'] #Characters to escape with a \
    text = str(text)
    for i in toEscape:
        text = text.replace(i, '\\'+i)
    return text.rstrip()
def tellRaw(text, frmTxt=None, to='@a'): #Runs the tellraw commands, and adds a "from" text if frmTxt is not None (with a from text would look like: <"frmTxt"> "text")
    if (to == ccRootUsr) or (ccRootUsr in str(frmTxt)) or (ccRootUsr in text):
        if frmTxt != None:
            print (frmTxt+' > "'+text+'"')
        else:
            print (' > "'+text+'"')
        return
    text = safeTellRaw(text).split('\n')
    if frmTxt != None:
        frmTxt = safeTellRaw(frmTxt)
        for i in text:
            writeCommand('tellraw '+to+' "<'+frmTxt+'> '+i+'"')
            print ('"'+frmTxt+'" > "'+i+'" > "'+to+'"')
    else:
        for i in text:
            writeCommand('tellraw '+to+' "'+i+'"')
            print (' > "'+i+'" > "'+to+'"')

#  Output parsing
def parseOutput(line): #Parses the output, running subfunctions for logging and parsing chat
    if len(line) == 0: #In case of empty line
        print ('Not parsing empty line (length 0)')
    elif line[0] != '[': #Unusual, means that there is no [HH:MM:SS] in front of message
        logData(line, 'Unusual+Errors')
    elif (line[9:12] == '] [') and (line[11:].split('/')[1][:5] in {'WARN]', 'ERROR', 'FATAL'}): #It's an error!
        logData(line, 'Unusual+Errors')
    elif ('*' in line) or ('<' in line): #Check these before parsing chat, since they use up less resources, and any chat message has to have either a < or a *
        if line[33] in {'*', '<'}:
            chatL = parseChat(line)
            if chatL[0] != 0:
                logData(line, 'RawChat') #Save line directly to raw chat log
                if chatL[0] == 1: #Is a regular chat message
                    logData('"'+chatL[1]+'" said "'+chatL[2]+'"', 'Chat') #Save formatted chat to chat log: "[User]" said "[Message]"
                    if chatL[2].startswith(chatComPrefix): #If it is a ChatCommand
                        parseChatCommand(chatL[1], chatL[2])
                        #return False #Stop checking output
                elif chatL[0] == 2: #Is a /me message
                    logData('"'+chatL[1]+'" me-ed "'+chatL[2]+'"', 'Chat') #Save formatted chat to chat log: "[User]" me-ed "[Message]"
                elif chatL[0] == 3: #Is a /say message
                    logData('"'+chatL[1]+'" /said "'+chatL[2]+'"', 'Chat')
            if profanity.contains_profanity(chatL[1]): #Chat message contains profanity, warn user
                tellRaw('<'+chatL[0]+'> '+profanity.censor(chatL[1], '!'))
                tellRaw('Potential profanity detected and logged', '[Swore!]')
        elif line[33:42] == '[Server] ':
            chatL = line[42:]
            logData(line, 'RawChat')
            logData('"[Server]" said "'+chatL)
    elif ' '.join(line.split(' ')[2:]) == 'joined the game':
        usrJoined = line.split(' ')[1]
        writeCommand('tellraw @a '+usrJoinMSG.replace('{%USER}', usrJoined))
        tellRaw('Use "'+chatComPrefix+'help" for a list of ChatCommands!', None, usrJoined)
    if profanity.contains_profanity(line): #Line contains profanity, log to file
        logData(line, 'Profanity')
def parseChat(line): #Get the chat / /me message and username out of a console line
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
                return [1, username, message]  #1=is a chat message
            elif line[33] == '*': #It is a /me message! (Who actually uses those???)
                line = line[35:].split(' ')
                username = line[0]
                message = ' '.join(line[1:])
                return [2, username, message] #2=is a /me message
            elif line[33] == '[': #It is a /say message!
                line = line[34:].split('] ')
                username = line[0]
                message = '] '.join(line[1:])
                return [3, username, message]
    return [0] #0=not a chat or /me message

# ChatCommands

#  Variables
chatCommandsLastUsed = {}

#   Help variables (help text keys in-game will be organized by the order by they are defined)
chatCommandsHelp = { #Help for regular ChatCommands that any user can run
    'help [command*]': 'Show help (this page) or help about optional [command]',
    'emoticons': 'Shows a list of copyable emoticons (specified by the server owner)',
    'size': 'Get the total size of the server world folder',
    'speedtest': 'Runs an internet speed test (has a 10 minute cooldown)', #Anything with a cooldown will be bypassed by admins, although the cooldown will also be reset
    'sysinfo | info': 'Shows some system information, such as memory and cpu usage',
    'tps': 'Shows the TPS (has a 2 minute cooldown)',
    'uptime': 'Show how long the server has been online since last restart',
}
chatCommandsHelpAdmin = { #Help for administrator commands that only admins and the server console can run
    'help [command*]': 'Show help (this page) or help about optional [command]',
    'ban [player] [reason*]': 'Ban [player] for optional [reason]',
    'crash [player] [severity*=3, 1-5]': 'Crashes the target player\'s game. Optional argument severity (default 3) chooses how "severe" the crash is (as well as how long it takes before the command is finished)',
    'kick [player] [reason*]': 'Kick [player] for optional [reason]',
    'reconfig': 'Reloads configuration from files',
    'logs {total}': 'Show how many logs have been collected (since last server restart, or since last shutdown if {total} is specified)',
    'refresh': 'Refreshes RunServerDotPy, reloading config and script. The server has to go offline during this time',
    'reload': 'Reloads all datapacks and assets (/reload command)',
    'restart | stop [reason*]': 'Restart the server for optional [reason]',
    'unban | pardon [player]': 'Unban/pardon [player]',
    'update | upgrade {dist,clean,pip}': 'Runs "apt-get update" and "apt-get upgrade" (also runs "apt-get dist-upgrade" if specified by flag {dist}, auto-cleans for flag {clean}, and attempts to upgrade pip modules for flag {pip}). ChatCommands will be paused while this is running',
}
chatCommandsHelpRoot = { #Help for root commands that only the server console can run
    'help [command*]': 'Show help (this page) or help about optional [command]',
    'clearlogs': 'Delete all logs, and resets the current log files',
    'py [command]': 'Runs the [command] in Python and returns output',
}

#    Remove unusable help strings
if os.name == 'nt':
    del chatCommandsHelpAdmin['update | upgrade {dist,clean,pip}']

#   Configuration variables
sysInfoShown = {
    'cpu': True,
    'memory': True,
    'temp': True,
    'battery': True,
    'diskrw': True,
}
if not hasattr(psutil, 'sensors_battery'):
    sysInfoShown['battery'] = False
if not hasattr(psutil, 'sensors_temperatures'):
    sysInfoShown['temp'] = False

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
            if user == ccRootUser: #User has permissions, run command
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
        chatCommandsLastUsed.setdefault(user, -1)
        if time.monotonic()-chatCommandsLastUsed[user] < 10:
            writeCommand('kick '+user+' SpamProtection: Please wait 1 second between ChatCommands')
            #tellRaw('Please wait 1 second, '+user, 'SpamProtection', user)
        else:
            runChatCommand(cmd, args, user)
        if chatCommandsLastUsed[user] != -1: #User is not an admin
            chatCommandsLastUsed[user] = time.monotonic()

#   ChatCommand subfunctions
def cc_help(ccHelpDict, args, ccPref=chatComPrefix, user='', toConsole=False): #If "toConsole" is True, then this just prints it. Otherwise, it uses a tellraw command
    if not len(args):
        command = None
    else:
        command = ' '.join(args)
    if command == None:
        cHelp = 'List of commands:\n("command" | "variation" ["positional arg(s) *=optional"] {"flags"}\n(Command prefix: '+ccPref+')\n(Use '+ccPref+'help [command] for help on a specific command)'
    else:
        cHelp = 'Help page for commands matching "'+command+'":'
    if toConsole:
        print (cHelp)
    else:
        tellRaw(cHelp, 'Help', user)
    showAll = (command == None) #Save a bit of time from calculations
    for i in ccHelpDict.keys():
        if showAll:
            if toConsole:
                print (' • '+i)
            else:
                tellRaw(' • '+i, None, user)
        else:
            if command in i:
                if toConsole:
                    print (' • '+i+': '+ccHelpDict[i])
                else:
                    tellRaw(' • '+i+': '+ccHelpDict[i], None, user)
def cc_parseSpeedTest(res):
    res = json.loads(res)
    down = makeValues(res['download'], 1024, sizeVals)
    up = makeValues(res['upload'], 1024, sizeVals)
    tellRaw(parseMadeValues(down)+' download', 'SpeedTest')
    tellRaw(parseMadeValues(up)+' upload', 'SpeedTest')
def cc_tellrawEmoticons(user):
    tellRaw('Click on an emoticon to copy it to your clipboard!', ' :) ', user)
    tellRaw('Multi-character emoticons:', ' :) ', user)
    for i in emoticons[1]:
        writeCommand('tellraw '+user+' {"text":"{%EMOTICON}","clickEvent":{"action":"copy_to_clipboard","value":"{%EMOTICON}"},"hoverEvent":{"action":"show_text","contents":[{"text":"{%EMOTICON}","bold":true}]}}'.replace('{%EMOTICON}', i))
        time.sleep(emoticons[0])
    tellRaw('Single-character emoticons:', ' :) ', user)
    for i in emoticons[2]:
        emotiComs = []
        for j in i:
            emotiComs.append('{"text":"{%EMOTICON}","clickEvent":{"action":"copy_to_clipboard","value":"{%EMOTICON}"},"hoverEvent":{"action":"show_text","contents":[{"text":"{%EMOTICON}","bold":true}]}}'.replace('{%EMOTICON}', j))
        writeCommand('tellraw '+user+' ['+(',{"text":" | "},'.join(emotiComs))+']')
        time.sleep(emoticons[0])
crashParticles = ['minecraft:elder_guardian', 'minecraft:sweep_attack', 'minecraft:explosion']
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

#   Basic functions (any user can run)
def runChatCommand(cmd, args, user):
    tellRaw('Running ChatCommand '+cmd, '$'+user)
    if cmd == 'help': #Displays a list of commands, or details for a specific command if arguments are specified
        cc_help(chatCommandsHelp, args, user=user)
    elif cmd == 'emoticons':
        threading.Thread(target=cc_tellrawEmoticons, args=(user,), daemon=True).start()
    elif cmd == 'nuke': #Secret command
        cc_crashPlayer(user, 1)
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
        if sysInfoShown['cpu']:
            tellRaw(str(psutil.cpu_percent())+'% of CPU used', None, user)
        if sysInfoShown['memory']:
            tellRaw(str(psutil.virtual_memory().percent)+'% of memory used', None, user)
        if sysInfoShown['temp']:
            temps = psutil.sensors_temperatures()
            for i in temps:
                t = 0
                for j in temps[i]:
                    t += j.current
                t = t/len(temps[i])
                if tempUnit[0] == 2:
                    t += 273.15
                elif tempUnit[0] == 1:
                    t = (t*(9/5))+32
                tellRaw('Temperature "'+i+'" is '+str(t)+tempUnit[1], None, user)
        if sysInfoShown['battery']:
            tellRaw('Battery has '+str(psutil.sensors_battery().percent)+'% charge (Plugged in: '+('yes' if psutil.sensors_battery().power_plugged else 'no')+')', None, user)
        if sysInfoShown['diskrw']:
            ioCount = psutil.disk_io_counters()
            tellRaw('Disk has had a total '+parseMadeValues(makeValues(ioCount.read_bytes, 1024, sizeVals))+' reads and '+parseMadeValues(makeValues(ioCount.write_bytes, 1024, sizeVals))+' writes since the last system restart')
    elif cmd == 'tps': #Gets the server's TPS over 10 seconds
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

#   Sudo/admin commands (only admins or server console can run these commands)
def runAdminChatCommand(cmd, args, user):
    tellRaw('Running SuperUser ChatCommand '+cmd, '$'+user, user)
    if cmd == 'help':
        cc_help(chatCommandsHelpAdmin, args, chatComPrefix+'sudo', user)
    elif cmd == 'ban':
        if len(args) > 1:
            tellRaw('Banning '+args[0]+' for '+(' '.join(args[1:])), 'Ban', user)
        else:
            tellRaw('Banning '+args[0], 'Ban', user)
        writeCommand('ban '+(' '.join(args)))
        if len(args) > 1:
            tellRaw(args[0]+' was banned for '+(' '.join(args[1]))+' by '+user, 'Ban')
        else:
            tellRaw(args[0]+' was banned by '+user, 'Ban')
    elif cmd == 'crash':
        target = args[0]
        if len(args) > 1:
            severity = int(args[1])
            if severity < 1 or severity > 5:
                tellRaw('Severity cannot be more than 5 or less than 1', 'Crasher', user)
                return
        else:
            severity = 3
        tellRaw('Crashing player '+target+' with severity '+str(severity), 'Crasher', user)
        threading.Thread(target=cc_crashPlayer, args=(target,severity), daemon=True).start()
        'crash [player] [severity*=3, 1-5]'
    elif cmd == 'kick':
        if len(args) > 1:
            tellRaw('Kicking '+args[0]+' for '+(' '.join(args[1:])), 'Kick', user)
        else:
            tellRaw('Kicking '+args[0], 'Ban', user)
        writeCommand('kick '+(' '.join(args)))
    elif cmd == 'logs':
        if 'total' in args:
            tellRaw('Logged amount over '+str(restarts)+' restarts:\n'+str(loggedAmountTotal), 'Logs', user)
        else:
            tellRaw('Logged amount for this iteration:\n'+str(loggedAmountIter), 'Logs', user)
    elif cmd == 'reconfig':
        tellRaw('Reloading configuration...', 'Config', user)
        loadConfiguration()
        tellRaw('Done', 'Config', user)
    elif cmd == 'refresh':
        tellRaw('Refreshing server...', user)
        runAdminChatCommand('stop', [], user) #Manually calls the "stop" admin ChatCommand with the user as the executor
        print ('Unhooking keyboard...')
        keyboard.unhook_all()
        while process.poll() == None: #Get remaining output while the process is still running
            getOutput(process)
        try:
            process.wait() #Wait for the process to complete
            print (process.stdout.read().decode('UTF-8')) #Read any leftover messsages and flush buffer
        except:
            pass
        finalizeLogFile() #Finalize the log file
        closeOpenFileHandles() #Important, because command below leaves file handles open
        print ('Goodbye')
        os.execl(sys.executable, sys.executable, *sys.argv) #Immediately replace the current process with this one, retaining arguments
    elif cmd == 'reload':
        tellRaw('Reloading!', None, user)
        writeCommand('reload')
    elif cmd in {'restart', 'stop'}:
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
    elif cmd in {'unban', 'pardon'}:
        tellRaw('Unbanning '+(' '.join(args[0])), 'Pardon', user)
        writeCommand('pardon '+(' '.join(args)))
    elif (os.name != 'nt') and (cmd in {'update', 'upgrade'}):
        #runWFullOutput(cmd, callbackFunc, callbackFuncXtraArgs=[])
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
            tellRaw('Done', 'AutoClean')
        if 'pip' in args:
            tellRaw('Updating PIP packages...', 'PIP')
            cmd = sys.executable+' -m pip list --outdated --format=freeze | grep -v \'^\\-e\' | cut -d = -f 1e'
            tellRaw(cmd)
            runWFullOutput(cmd, tellRaw)
            tellRaw('Done', 'PIP')
        del cmd

#   Root commands (only server console can run these commands)
def runRootChatCommand(cmd, args):
    print ('$ Running Root ChatCommand '+cmd)
    if cmd == 'help':
        cc_help(chatCommandsHelpRoot, args, chatComPrefix+'root', '', True)
    elif cmd == 'clearlogs':
        print (cmd)
    elif cmd == 'py':
        print (cmd)

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
            inputQueue.put('[##:##:##] [Server thread/INFO]: <'+ccRootUsr+'> '+line, False)
            writeCommand('')
        else: #Otherwise pass it to the server console as normal
            print ('> '+line)
            writeCommand(line)
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
    if os.name == 'nt':
        print ('Cannot run auto-backup on Windows')
    else:
        print ('Starting auto-backup...')
        cwd = os.getcwd()
        os.chdir(srvrFolder+'..') #Change to directory directly outside of server folder, so that the zip file has everything without a bunch of extra directory structure
        os.system('zip -q -r -FS -9 '+autoBckpZip+' '+os.path.basename(srvrFolder))
        os.chdir(cwd) #Go back to previous working directory to prevent conflicts
def swapIcon():
    print ('Swapping server icon...')
    if len(serverIcons) > 0:
        svrIco = random.choice(serverIcons)
        print ('Selected server icon:\n'+os.path.basename(srvIco)+'\nSwapping...')
        shutil.copy(srvIco, srvrFolder+'server-icon.png') #Copy over new server icon
        print ('Done')
    else: #If there are no server icons to choose from
        print ('\nNO *.png SERVER ICONS PRESENT! ADD SOME IN '+iconsDir+'!\n')
def swapMOTD(uptimeStart): #MOTD = message of the day
    print ('Swapping MOTD...')
    if len(motds) > 0:
        motd = random.choice(motds)
        motd += '\\u00A7r\\n\\u00A7o(Last restart: \\u00A7n'+(time.ctime(uptimeStart).rstrip().replace('  ', ' '))+'\\u00A7r\\u00A7o)' #Add timestamp to MOTD
        print ('Selected MOTD:\n'+motd+'\nReading properties...')
        with open('server.properties') as pf: #Read the properties
            props = pf.read().split('\n')
        print ('Adding MOTD to properties and writing back to file...')
        for i in range(len(props)): #Add the MOTD to the properties
            if props[i].startswith('motd='):
                props[i] = 'motd='+motd
        with open('server.properties', 'w') as pf: #Write the modified properties back to the file
            pf.write('\n'.join(props))
        print ('Done')
    else: #If there are no MOTDs to choose from
        print ('\nNO MOTDs TO CHOOSE FROM! ADD SOME IN '+confDir+'motds.conf!\n')
def serverHandler(): #Wed Jul 28 13:53:08 2021
    global process
    #Setup timing variables
    global lastSpeedTest
    global lastTickTest
    global uptimeStart
    global lastEmoticonShow
    lastSpeedTest = -1
    lastTickTest = -1
    lastEmoticonShow = -1
    uptimeStart = time.monotonic()
    #Setup functions
    keyboard.unhook_all() #Unhook keyboard while processes are running
    autoBackup() #Automatically backup everything
    swapIcon() #Swap the server icon (if there are any present)
    swapMOTD(uptimeStart) #Swap the server MOTD (message of the day) (if there are any present)
    makeLogFile() #Setup logging
    closeOpenFileHandles() #Close any open file handles
    #Rehook keyboard
    rehookKeyboard()
    #Main server starting and handling
    startServer() #Start the main server
    time.sleep(1) #Give it a bit of time to boot
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
                    writeCommand('tellraw @a ["",{"text":"'+safeTellRaw(i)+'","bold":true,"color":"red"}]')
            except:
                print (traceback.format_exc())
        if process.poll() != None:
            break
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
            print (process.stdout.read().decode('UTF-8')) #Read any leftover messages and flush buffer
        except:
            pass
        try:
            for i in range(5, 0, -1): #Countdown from 5
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
