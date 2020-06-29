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

filePath = "[PATH TO YOUR SCRIPT]"
arcPath = "[PATH TO YOUR HERITRIX JOBS FOLDER]"
inputFile = "URLs.txt" #Path to the URL list.
heritrixUrl = "[URL TO YOUR HERITRIX WEB INTERFACE]"
heritrixLogin = "[YOUR HERITRIX USERNAME]"
heritrixPass = "[YOUR HERITRIX PASSWORD]"
jobID = "Monthly"

flawlessCreate = False
flawlessRun = False

#Specify the crawl ID

now = datetime.now()
dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
print(dt_string)
print("\nURLs found in list:\n")
lineList = [line.rstrip('\n') for line in open(inputFile)]

#Populate a job list with proper job names (name+ID)
jobList = []
for line in lineList:
    line = line.replace("http:","").replace("https:","").replace("/","")
    line = line + "-" + jobID
    print("- " + line)
    jobList.append(line)

post = requests.Session()

for idx, line in enumerate(jobList):

    #Create the job...
    print("Creating job '" + line + "'...", end = '')
    payload = {'createpath':line, 'action':'create'}
    post = requests.post(heritrixUrl, data=payload, auth=HTTPDigestAuth(heritrixLogin,heritrixPass), verify=False)
    if "200" in str(post.status_code):
        print("\033[92mDone!\033[0m")
        flawlessCreate = True
    else:
        print("\033[91mERROR!\033[0m: " + str(post.status_code))
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
    jobPath = arcPath + line + "/crawler-beans.cxml"
    outfile = open(jobPath,"a+")
    outfile.truncate(0)
    for line in baseFile:
        outfile.write(line + '\n')
    outfile.close()
    if path.exists(jobPath):
        print("\033[92mDone!\033[0m")
        flawlessCreate = True
    else:
        print("\033[91mERROR!\033[0m")
        flawlessCreate = False
if(flawlessCreate):
    print("All jobs created successfully!\n")
else:
    print("Encountered errors while creating jobs.")
        
for idx, line in enumerate(jobList):
      
    jobURL = heritrixUrl + "/job/" + line
    if not path.exists(arcPath + line):
        #Build the job...
        print("Building job " + line + "... ", end = '')
        payload = {'action':'build'}
        post = requests.post(jobURL, data=payload, auth=HTTPDigestAuth(heritrixLogin,heritrixPass), verify=False)
        if "200" in str(post.status_code):
            print("\033[92mDone!\033[0m")
            flawlessRun = True
        else:
            print("\033[91mERROR!\033[0m: " + str(post.status_code))
            flawlessRun = False
            
    #Launch the job...
    print("Launching job " + line + "... ", end = '')
    payload = {'action':'launch'}
    post = requests.post(jobURL, data=payload, auth=HTTPDigestAuth(heritrixLogin,heritrixPass), verify=False)
    if "200" in str(post.status_code):
        print("\033[92mDone!\033[0m")
        flawlessRun = True
    else:
        print("\033[91mERROR!\033[0m: " + str(post.status_code))
        flawlessRun = False

if flawlessRun:
    print("\nAll tasks completed \033[92mSUCCESSFULLY!\033[0m\nNow waiting for 48 hours before tearing down...")
    #Wait for 48 hours...
    time.sleep(172800)
else:
    print("Encountered errors during launching. Please view logs!")
    exit(1)
    
for idx, line in enumerate(jobList):
    jobURL = heritrixUrl + "/job/" + line
    #Teardown the jobs...
    print("Tearing down " + line + "... ", end = '')
    payload = {'action':'teardown'}
    post = requests.post(jobURL, data=payload, auth=HTTPDigestAuth(heritrixLogin,heritrixPass), verify=False)
    if "200" in str(post.status_code):
        print("\033[92mDone!\033[0m")
        flawlessRun = True
    else:
        print("\033[91mERROR!\033[0m: " + str(post.status_code))
        flawlessRun = False

#Print success status if nothing failed
if flawlessRun:
    print("\nMonthly crawls started and stopped \033[92mSUCCESSFULLY!\033[0m\n")
else:
    print("Encountered errors during launching. Please view logs!")