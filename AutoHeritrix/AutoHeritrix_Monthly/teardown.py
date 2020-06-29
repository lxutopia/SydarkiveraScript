import os.path
import requests
from os import path
from datetime import datetime
from requests.auth import HTTPDigestAuth
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

#Change working directory
#os.chdir("/home/AutoHeritrix_Monthly")

filePath = "[PATH TO YOUR SCRIPT]"
arcPath = "[PATH TO YOUR HERITRIX JOBS FOLDER]"
inputFile = "URLs.txt" #Path to the URL list.
heritrixUrl = "[URL TO YOUR HERITRIX WEB INTERFACE]"
heritrixLogin = "[YOUR HERITRIX USERNAME]"
heritrixPass = "[YOUR HERITRIX PASSWORD]"
jobID = "Monthly"

flawlessRun = False

#Specify the crawl ID

now = datetime.now()
dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
print(dt_string)
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
    print("\nAll tasks completed \033[92mSUCCESSFULLY!\033[0m\n")