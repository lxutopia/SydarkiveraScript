import os.path
import requests
from os import path
from requests.auth import HTTPDigestAuth
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

filePath = "[PATH TO YOUR SCRIPT]"
arcPath = "[PATH TO YOUR HERITRIX JOBS FOLDER]"
inputFile = "URLs.txt" #Path to the URL list.
heritrixUrl = "[URL TO YOUR HERITRIX WEB INTERFACE]"
heritrixLogin = "[YOUR HERITRIX USERNAME]"
heritrixPass = "[YOUR HERITRIX PASSWORD]"

flawless = False

#Specify the crawl ID
jobID = input("\nSpecify crawl ID (yyyymmdd): ")
print("\nURLs found in list:\n")
lineList = [line.rstrip('\n') for line in open(inputFile)]

#Populate a job list with proper job names (name+ID)
jobList = []
for line in lineList:
    line = line.replace("http:","").replace("https:","").replace("/","")
    line = line + "-" + jobID
    print("- " + line)
    jobList.append(line)
reply = input("\nCreate these jobs? (y/n): ")
if reply == "y" or reply == "Y":
    post = requests.Session()
    for idx, line in enumerate(jobList):
        
        #Create the job...
        print("Creating job '" + line + "'...", end = '')
        payload = {'createpath':line, 'action':'create'}
        post = requests.post(heritrixUrl, data=payload, auth=HTTPDigestAuth(heritrixLogin,heritrixPass), verify=False)
        if "200" in str(post):
            print("\033[92mDone!\033[0m")
            flawless = True
        else:
            print("\033[91mERROR!\033[0m: " + str(post.status_code))
            exit(1)
        
        #Edit local config file URL-line...    
        print("Configuring URL... ", end = '')
        baseFile = [line.rstrip('\n') for line in open(filePath + "crawler-beans-base.cxml")]
        marker = baseFile.index("# URLS HERE") + 1
        baseFile[marker] = baseFile[marker].replace(baseFile[marker],lineList[idx])
        if baseFile[marker] == lineList[idx]:
            print("\033[92mDone!\033[0m")
            flawless = True
        else:
            print("\033[91mERROR!\033[0m")
            exit(1)
        
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
            flawless = True
        else:
            print("\033[91mERROR!\033[0m")
            exit(1)
        
    reply = input("\nWould you like to run these jobs now? (y/n): ")
    if reply == "y" or reply == "Y":
        for idx, line in enumerate(jobList):
            jobURL = heritrixUrl + "/job/" + line
            
            #Build the job...
            payload = {'action':'build'}
            print("Building job " + line + "... ", end = '')
            post = requests.post(jobURL, data=payload, auth=HTTPDigestAuth(heritrixLogin,heritrixPass), verify=False)
            if "200" in str(post):
                print("\033[92mDone!\033[0m")
                flawless = True
            else:
                print("\033[91mERROR!\033[0m: " + str(post.status_code))
                flawless = False
            
            #Launch the job...
            payload = {'action':'launch'}
            print("Launching job " + line + "... ", end = '')
            post = requests.post(jobURL, data=payload, auth=HTTPDigestAuth(heritrixLogin,heritrixPass), verify=False)
            if "200" in str(post):
                print("\033[92mDone!\033[0m")
                flawless = True
            else:
                print("\033[91mERROR!\033[0m: " + str(post.status_code))
                flawless = False
        
        #Print success status if nothing failed
        if flawless == True:
            print("\nAll tasks completed \033[92mSUCCESSFULLY!\033[0m\n")
    else:
        print("Quitting...")
        exit()
else:
    print("Quitting...")
    exit()
