<!--- State the text needed in the fields marked with [explanatory on what] if not needed remove the text. 
Feel free to use more mark down for formatting the text-->
# AutoHeritrix

## Explanation of the software
AutoHeritrix is a software intended to automate the creation, building and launching of jobs in Heritrix 3.
The software uses Python Requests library to communicate with Heritrix REST API, launching jobs based on a list of URLs.

Please note that the software is intended to be run specifically in Sydarkiveras production environment. The software will not work properly without editing the code to fit other hardware- and software setups.

## Dependencies
This software is designed to run in a Linux environment, tested successfully on CentOS 7 (https://www.centos.org/).

For running this script there are dependencies to the following software libraires:

Running this software requires the following dependencies:

- Python 3 (https://www.python.org/)
- Requests library (https://requests.readthedocs.io/)
- Heritrix 3 (https://github.com/internetarchive/heritrix3)

A txt-file containing a list of URLs to be crawled is required as well as an XML-template for Heritrix configuration.
Please refer to the Heritrix 3 documentation for information on how to install and configure Heritrix.

## How to run the software
1.  Place the version of AutoHeritrix you intend to use, the template and the URL-list in a folder, for instance under /home.
2.  Make sure Heritrix 3 is running and properly configured to run jobs. Generally, if you can access the web interface, you're good to go.
3.	 Edit the URL-list, seperating each URL to be crawled on a new line.
4.  Edit the python script to fit your crawing environment. Please refer to the comments to understand what needs to be specified.
5.  Edit the template ```crawler-beans.xml```with your prefered crawl options.
6.  Run the software in your Python 3 environment: ```$ python3 AutoHeritrix.py```

Alternatively you can schedule AutoHeritrix to run using crontab: ```* * * *    /usr/bin/python3    /path/to/software/AutoHeritrixMonthly.py -new >> /path/to/logs/autoHeritrixLog.txt```

When the software runs the first time it will create an index file that keeps track of which URLs have been started in case of a crash or other issue.
If the index reaches its end you can start the software with ```-new``` to reset the index. This is recommended when AutoHeritrix runs through a cronjob.
>>>>>>> parent of a0bba0a (Merge branch 'AutoHeritrix' of https://github.com/PreAmbience/SydarkiveraScript into AutoHeritrix)

### AutoHeritrix2020.py
The 2020 version of AutoHeritrix allows for a manual launch through the command line and is meant for a smaller amount of crawls.
This version is no longer supported by Sydarkivera and does not support scheduling.

1.  Specify an ID for your crawls. The ID will be used to name the Heritrix jobs. For example, the current date.
2.  The software will list the URLs found in the URL-list combined with the ID you specified, after which you will be asked whether to create the jobs in Heritrix. Reply Y or N and press Return.
3.  Wait for the job creation to finish. If everything is set up properly you should now be able to see the jobs listed in the Heritrix web interface. Make sure to refresh the page if you don't. 
4.  The software will ask whether you want to build and run the jobs. Reply Y or N and press Return.
5.  Wait for the software to finish building and running the jobs. Make sure to check the Heritrix web interface to confirm whether the jobs have been started.
6. You're done!

Once jobs have been run, the script will let them run for 48 hours before performing a teardown on them to save resources and prepare them for the next build and run.
Teardowns can also be performed manually by running the script ```teardown.py```.

## Description by:
Magnus "PreAmbience" Heimonen, 2021-03-17
