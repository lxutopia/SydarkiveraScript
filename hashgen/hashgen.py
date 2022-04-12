import hashlib, os, getopt, sys, datetime

path = '.'
logPath = './logs'
fileType = ''
hashedObjects = []
readObjects = []
logObjects = []
regFilename = 'hashRegistry.txt'
newRun = False
debug = False
date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
spc = '    '
helpMessage = """
######################################
## HashGen by Magnus Heimonen, 2022 ##
######################################

HashGen helps to automate and streamline checksum generation and validation on all or selected filetypes.
Through the use of flags you may specify a search path, filetype to generate/validate and the name of the hash registry.

###Default usage

Running the software without flags will do nothing unless a registry already has been generated.
If a registry exists, the software will validate all files in the current work directory and subdirectories recursively against it.
If files have changed or been added/removed, the software will report this appropriately.
If a file fails to validate, the software will show the old checksum on the left and the new checksum on the right.

###Flags

-n  Default: Disabled
    New registry. This generates a new registry on the properties you specify.
    If you do not specify any other flags, the software will generate it on all files recursively from your work directory.

-f [filetype]   Default: All types
    Specify a search term to validate or generate a registry from with -n. For example .txt or .warc.gz
    Keep in mind that if you generate a registry with a filetype, you must keep the flag for future validations for that specific filetype.

-p [path]   Default: Work directory
    Specify a path to check for files in.

-o [path/filename]  Default: hashRegistry.txt
    Output. Specify the name/location of the output file.
    
-l [path]   Default: Work directory
    Logging. Specify in which folder you want the generated validation logs to be placed. Logs will be named with the current date and filetype.
    It is recommended to use this instead of redirecting output to a file!
    
-d  Default: Disabled
    Debug. Shows verbose messages for each stage in the validation process.
    
-h
    Help. Shows this help message."""

#Read input options   
argv = sys.argv[1:]
opts, args = getopt.getopt(argv, "hnp:f:o:dl:")
for opt, arg in opts:
    if opt in ['-n']:
        newRun = True
    if opt in ['-p']:
        path = arg
    if opt in ['-f']:
        fileType = arg
    if opt in ['-h']:
        print(helpMessage)
        sys.exit()
    if opt in ['-o']:
        regFilename = arg
    if opt in ['-d']:
        debug = True
    if opt in ['-l']:
        logPath = arg

#Read file contents
if not newRun:
    print('\nValidating...\033[F')
    try:
        with open(regFilename, 'r') as regFile:
            if debug: print("File contents: \n")
            for line in regFile.read().split('\n'):
                if line and fileType in line:
                    if debug: print(line)
                    readObjects.append({'checksum':line.split(spc)[0],'filename':line.split(spc)[1]})
    except:
        print(helpMessage)
        sys.exit()

#Generate a list of hashes
if debug: print("\nGenerated hashes: \n")
for root, dirs, files in os.walk(path):
    for file in files:
        if not file in (regFilename,'hashgen.py') and fileType in file:
            h = hashlib.md5()
            h.update(open(os.path.join(root,file), 'rb').read())
            if newRun or debug:
                print(h.hexdigest() + spc + os.path.join(root,file))
            hashedObjects.append({'checksum':h.hexdigest(),'filename':os.path.join(root,file)})
if not hashedObjects:
    print('No matches for filename ' + fileType + ' found.')
    sys.exit()

#Validate the contents of the registry
if not newRun:
    if debug: print("\nValidation: \n")
    ln = '[' + date + ']'
    print(ln)
    logObjects.append(ln + '\n')
    for line in readObjects:
        if line in hashedObjects:
            ln = line['checksum'] + spc + '[VALID]' + spc + line['filename']
            print(ln)
            logObjects.append(ln + '\n')
        else:
            match = ''
            for matchline in hashedObjects:
                if matchline['filename'] in line['filename']:
                    match = 'NEW CHECKSUM: ' + matchline['checksum']
                    msg = 'NOT VALID'
                    break
                else:
                    msg = 'REMOVED'
                    match = ''
            ln = line['checksum'] + spc + '[' + msg + ']' + spc + line['filename'] + spc + match
            print(ln)
            logObjects.append(ln + '\n')

#Print file changes
if not newRun:
    newFiles = [line for line in hashedObjects if line['filename'] not in [match['filename'] for match in readObjects]]
    removedFiles = [line for line in readObjects if line['filename'] not in [match['filename'] for match in hashedObjects]]
    if debug: print('\nNew/Removed:\n\n' + str(newFiles) + '\n\n' + str(removedFiles))
    if newFiles or removedFiles:
        ln = "\nFiles have changed. Registry has " + str(len(readObjects)) + " lines. Detected " + str(len(hashedObjects)) + " files."
        print(ln)
        logObjects.append(ln + '\n')
        if newFiles:
            ln = '\n' + str(len(newFiles)) + ' UNREGISTERED FILE(S):\n'
            print(ln)
            logObjects.append(ln)
            for files in newFiles:
                ln = files['checksum'] + spc + files['filename']
                print(ln)
                logObjects.append(ln + '\n')
        if removedFiles:
            ln = '\n' + str(len(removedFiles)) + ' REMOVED FILE(S):\n'
            print(ln)
            logObjects.append(ln)
            for files in removedFiles:
                ln = files['checksum'] + spc + files['filename']
                print(ln)
                logObjects.append(ln + '\n')

#Write logs
if logObjects:
    if fileType: logdate = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + '_' + fileType
    else: logdate = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    if not os.path.isdir(logPath): os.mkdir(logPath)
    with open(logPath + '/' + logdate + '.log', 'w') as logFile:
        for line in logObjects:
            logFile.write(line)

#Write registry
if newRun:
    with open(regFilename, 'w') as regFile:
        for line in hashedObjects:
            regFile.write(line['checksum'] + spc + line['filename'] + '\n')