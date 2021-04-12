import os.path
import requests
import time
import sys
import getopt
from datetime import datetime
from requests.auth import HTTPDigestAuth
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Default configuration
filePath = "" #The path of the .cxml template for all crawls, usually "crawler-beans-base.cxml"
jobID = "" #The appended ID of the job
inputFile = "URLs.txt" #Usually a txt file with all the URLs to be crawled
heritrixUrl = "" #The URL to the Heritrix engine
heritrixUser = "" #Username for Heritrix authentication
heritrixPass = "" #Password for Heritrix authentication
jobLimit = 10 #Amount of jobs allowed to run at any one time
waitTime = 21600 #Amount of SECONDS the program should wait before looping, default 6 hours
finished = 0
running = 0
finList = []
jobList = []
newRun = False

session = requests.Session()

starttime = datetime.now()

## CHECK ARGUMENTS ##################################
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "i:a:u:p:f:w:l:d:n")
    for opt, arg in opts:
        if opt in ['-i']:
            jobID = arg
        elif opt in ['-a']:
            heritrixUrl = arg
        elif opt in ['-u']:
            heritrixUser = arg
        elif opt in ['-p']:
            heritrixPass = arg
        elif opt in ['-f']:
            inputFile = arg
        elif opt in ['-w']:
            waitTime = int(arg)
        elif opt in ['-l']:
            jobLimit = int(arg)
        elif opt in ['-n']:
            newRun = True
        elif opt in ['-d']:
            os.chdir(arg)
except:
    print("Error in arguments. Quitting...")
    sys.exit()

## CHECK URL LIST ###################################
try:
    lineList = [line.rstrip('\n') for line in open(inputFile)] 
    if len(lineList) == 0:
        sys.exit("\033[91mURL list is empty. Exiting.\033[0m")
except FileNotFoundError:
    sys.exit("\033[91mCannot find URL list. Specify one with -f 'name'\033[0m")

## CHECK HERITRIX ###################################
try:
    session = requests.get(heritrixUrl, auth=HTTPDigestAuth(heritrixUser,heritrixPass), verify=False)
    if "200" in str(session.status_code) and "heritrixVersion" in session.text:
        print("\033[92mConnected to Heritrix engine.\033[0m")
    elif "200" in str(session.status_code) and "heritrixVersion" not in session.text:
        sys.exit("\033[91mSpecified URL is not a Heritrix engine URL!\033[0m\nPlease make sure you have entered the correct URL!")
    elif "401" in str(session.status_code):
        sys.exit("\033[91mCannot authenticate with Heritrix!\033[0m Error: 401\nPlease make sure you have entered the correct username and password!")
except ConnectionRefusedError:
    sys.exit("\033[91mCannot connect to Heritrix!\033[0m \nPlease make sure Heritrix engine is running and you have entered the correct URL!")
except requests.ConnectionError:
    sys.exit("\033[91mCannot connect to Heritrix!\033[0m \nPlease make sure Heritrix engine is running and you have entered the correct URL!")

## CREATE INDEX FILE IF MISSING #####################
if not os.path.exists("index") or newRun == True:
    print("Creating / resetting index file.")
    with open("index","w") as indexFile:
        indexFile.write("0")

## READ INDEX FILE ##################################
with open("index","r") as indexFile:
    jobIndex = int(indexFile.read())
    #Populate a job list with proper job names (name+ID)
    if jobIndex < len(lineList):
        print("\n\033[4mLISTED URLS - " + str(len(lineList)) + "\033[0m")
        for idx, line in enumerate(lineList):
            line = line.replace("http:","").replace("https:","").replace("/","")
            if line != '':
                print("[" + str(idx + 1) + '] ' + line)
            jobList.append(line)
    else:
        print("\n\033[92mReached end of URL index.\033[0m\nIf you want to start over, please run the program with the argument -n\nAutoHeritrix will continue performing teardowns until all jobs have finished.")
        
## GET CURRENT HERITRIX STATUS ######################
def getStatus():
    global finished, running, finList, available
    session = requests.get(heritrixUrl, auth=HTTPDigestAuth(heritrixUser,heritrixPass), verify=False)
    output = session.content.decode().split()
    finished = 0
    running = 0
    finList.clear()
    for i in range(len(output)):
        if '<crawlControllerState>FINISHED</crawlControllerState>' in output[i]:
            finished += 1
            finList.append(output[i - 11].replace('<shortName>','').replace('</shortName>',''))
        if '<crawlControllerState>RUNNING</crawlControllerState>' in output[i]:
            running += 1
    print("Running: " + str(running) + '\nFinished: ' + str(finished))
    available = jobLimit - running

## TEAR DOWN FINISHED JOBS ###########################
def teardown():
    global finished, currentJob, finList
    for line in finList:
        jobURL = heritrixUrl + "/job/" + line
        #Teardown the jobs...
        print("Tearing down " + line + "... ", end = '')
        payload = {'action':'teardown'}
        session = requests.post(jobURL, data=payload, auth=HTTPDigestAuth(heritrixUser,heritrixPass), verify=False)
        if "200" in str(session.status_code):
            print("\033[92mDone!\033[0m")
        else:
            print("\033[91mERROR!\033[0m: " + str(session.status_code))
    finList.clear()

### START AVAILABLE JOBS #############################
def startJob(dt_short):
    global jobList, jobID, jobIndex, heritrixUrl, available
    date = dt_short
    flawlessRun = False
    i=0
    try:
        while i < available:
            if len(jobID) > 0:
                currentJob = jobList[jobIndex] + '-' + jobID
            else:
                currentJob = jobList[jobIndex] + '-' + date
            jobURL = heritrixUrl + "/job/" + currentJob
            steps = 1
            #Create the job...
            print("Starting job [\033[97m" + str(jobIndex + 1) + "\033[0m] " + currentJob + "... ", end = '')
            payload = {'createpath':currentJob, 'action':'create'}
            session = requests.post(heritrixUrl, data=payload, auth=HTTPDigestAuth(heritrixUser,heritrixPass), verify=False)
            if "200" in str(session.status_code):
                steps = steps + 1
            
            #Edit local config file URL-line...    
            baseFile = [line.rstrip('\n') for line in open(filePath + "crawler-beans-base.cxml")]
            marker = baseFile.index("# URLS HERE") + 1
            baseFile[marker] = baseFile[marker].replace(baseFile[marker],lineList[jobIndex])
            if baseFile[marker] == lineList[jobIndex]:
                steps = steps + 1
            
            #Send new config file to job... 
            configUrl = heritrixUrl + "/job/" + currentJob + "/jobdir/crawler-beans.cxml"
            session = requests.put(configUrl, data='\n'.join(baseFile), auth=HTTPDigestAuth(heritrixUser,heritrixPass), verify=False)
            if "200" in str(session.status_code):
                steps = steps + 1
                
            #Build the job...
            payload = {'action':'build'}
            session = requests.post(jobURL, data=payload, auth=HTTPDigestAuth(heritrixUser,heritrixPass), verify=False)
            if "200" in str(session.status_code):
                steps = steps + 1
                    
            #Launch the job...
            payload = {'action':'launch'}
            session = requests.post(jobURL, data=payload, auth=HTTPDigestAuth(heritrixUser,heritrixPass), verify=False)
            if "200" in str(session.status_code):
                steps = steps + 1
                
            #Everything went well
            if steps == 6:
                print("\033[92mOK\033[0m")
            #If not, print error
            elif steps == 1:
                print("\033[91mERROR!\033[0m Creation failed.")
            elif steps == 2:
                print("\033[91mERROR!\033[0m Configuration failed.")
            elif steps == 3:
                print("\033[91mERROR!\033[0m Send failed.")
            elif steps == 4:
                print("\033[91mERROR!\033[0m Build failed.")
            elif steps == 5:
                print("\033[91mERROR!\033[0m Launch failed.")
             
            available -= 1
            jobIndex += 1
    except IndexError:
        print("\n\033[92mReached end of URL index.\033[0m\nIf you want to start over, please run the program with the argument -n\nAutoHeritrix will continue performing teardowns until all jobs have finished.")
        pass

## MAIN LOOP #########################################
mainLoop = True
while mainLoop:
    now = datetime.now() #Get current time and date
    dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
    dt_short = now.strftime("%Y%m%d")
    print("\n\033[4m" + dt_string + "\033[0m\nCurrent index: " + str(jobIndex) + " of " + str(len(lineList)))
    getStatus() #Get current heritrix status
    if finished > 0:
        teardown() #Tear down existing jobs
    print("Available slots: " + str(available) + '\n')
    if jobIndex < len(jobList) and available > 0:
        startJob(dt_short) #Start new jobs
        with open("index","r+") as indexFile:
            indexFile.write(str(jobIndex)) #Write current index to file
    if jobIndex >= len(jobList) and available == jobLimit:
        endtime = now - starttime
        sys.exit("\033[92mAll URLs crawled in " + str(endtime.days) + " days\033[0m - Exiting AutoHeritrix.")
    time.sleep(waitTime)
