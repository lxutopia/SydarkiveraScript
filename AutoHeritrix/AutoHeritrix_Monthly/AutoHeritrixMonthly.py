import os.path
import requests
import time
from os import path
from datetime import datetime
from requests.auth import HTTPDigestAuth
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

#Change working directory if needed
#os.chdir("/home/AutoHeritrix_Monthly")

filePath = "" #The path of the .cxml template for all crawls, usually "crawler-beans-base.cxml"
jobID = "" #The appended ID of the job
arcPath = "" #The path to Heritrix jobs directory
inputFile = "" #Usually a txt file with all the URLs to be crawled
heritrixUrl = "" #The URL to the Heritrix engine
heritrixUser = "" #Username for Heritrix authentication
heritrixPass = "" #Password for Heritrix authentication
jobsAllowed = 10 #Amount of jobs allowed to run at any one time
waitTime = 21600 #Amount of SECONDS the program should wait before looping
initialStart = True

finished = 0
running = 0
jobIndex = 0
finList = []
jobList = []
lineList = [line.rstrip('\n') for line in open(inputFile)]  

session = requests.Session()

#################################
def getStatus():
    global finished, running, finList, available, heritrixUser, heritrixPass, jobsAllowed
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
    available = jobsAllowed - running


################################
def teardown():
    global finished, currentJob, finList, heritrixUser, heritrixPass
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


################################
def startJob():
    global jobList, jobID, jobIndex, arcPath, heritrixUrl, available, heritrixUser, heritrixPass
    now = datetime.now()
    dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
    flawlessRun = False

    i=0
    try:
        while i < available:
            #Create the job...
            print("Creating job '" + jobList[jobIndex] + "'...", end = '')
            payload = {'createpath':jobList[jobIndex], 'action':'create'}
            session = requests.post(heritrixUrl, data=payload, auth=HTTPDigestAuth(heritrixUser,heritrixPass), verify=False)
            if "200" in str(session.status_code):
                print("\033[92mDone!\033[0m")
                flawlessCreate = True
            else:
                print("\033[91mERROR!\033[0m: " + str(session.status_code))
                flawlessCreate = False
            
            #Edit local config file URL-line...    
            print("Configuring URL... ", end = '')
            baseFile = [line.rstrip('\n') for line in open(filePath + "crawler-beans-base.cxml")]
            marker = baseFile.index("# URLS HERE") + 1
            baseFile[marker] = baseFile[marker].replace(baseFile[marker],lineList[idx])
            if baseFile[marker] == lineList[idx]:
                print("\033[92mDone!\033[0m")
                flawlessCreate = True
            else:
                print("\033[91mERROR!\033[0m")
                flawlessCreate = False
            
            #Send new config file to job...    
            print("Writing config file... ", end = '')
            jobPath = arcPath + jobList[jobIndex] + "/crawler-beans.cxml"
            print(jobPath)
            outfile = open(jobPath,"a+")
            outfile.truncate(0)
            for line in baseFile:
                outfile.write(jobList[line] + '\n')
            outfile.close()
            if path.exists(jobPath):
                print("\033[92mDone!\033[0m")
                flawlessCreate = True
            else:
                print("\033[91mERROR!\033[0m")
                flawlessCreate = False
                
            jobURL = heritrixUrl + "/job/" + jobList[jobIndex]
            if not path.exists(arcPath + jobList[jobIndex]):
                #Build the job...
                print("Building job " + jobList[jobIndex] + "... ", end = '')
                payload = {'action':'build'}
                session = requests.post(jobURL, data=payload, auth=HTTPDigestAuth(heritrixUser,heritrixPass), verify=False)
                if "200" in str(session.status_code):
                    print("\033[92mDone!\033[0m")
                    flawlessRun = True
                else:
                    print("\033[91mERROR!\033[0m: " + str(session.status_code))
                    flawlessRun = False
                    
            #Launch the job...
            print("Launching job " + jobList[jobIndex] + "... ", end = '')
            payload = {'action':'launch'}
            session = requests.post(jobURL, data=payload, auth=HTTPDigestAuth(heritrixUser,heritrixPass), verify=False)
            if "200" in str(session.status_code):
                print("\033[92mDone!\033[0m")
                flawlessRun = True
            else:
                print("\033[91mERROR!\033[0m: " + str(session.status_code))
                flawlessRun = False

            available -= 1
            jobIndex += 1
    except IndexError:
        print("Reached end of URL index.")
        pass

########################### MAIN LOOP ##################

print("\nURLs found in list:\n")
#Populate a job list with proper job names (name+ID)

for idx, line in enumerate(lineList):
    line = line.replace("http:","").replace("https:","").replace("/","")
    line = line + "-" + jobID
    if line != '':
        print(str(idx) + " - " + line)
    jobList.append(line)


mainLoop = True
print(len(jobList))
while mainLoop:
    now = datetime.now()
    dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
    print("\n\n" + dt_string + "\nCurrent index: " + str(jobIndex))
    getStatus()
    if finished > 0:
        teardown()
    print("Available slots: " + str(available))
    if available > 0:
        startJob()
    if jobIndex >= len(jobList):
        mainLoop = False
    initialStart = False
    time.sleep(waitTime)


