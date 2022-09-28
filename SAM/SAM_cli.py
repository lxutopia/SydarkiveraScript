import sys, os, hashlib, re, getopt
from pathlib import Path
from cryptography.fernet import Fernet

scriptpath = os.path.abspath(sys.argv[0])
scriptpath = os.path.dirname(scriptpath)

mergedPath = ''
partsPath = ''
filename = ''
filepath = ''
inputFile = ''
cryptfile = ''
inputSize = 200
logOutput = []
spc = '    '
encrypt = False

def fileCombine():
    global inputFile, inputSize, mergedPath, partsPath
    #If parts are specified, combine the parts
    print('\nMerging operation started\n')
    if not mergedPath:
            print("Merged folder not specified. Proceeding with default ./merged/")
            mergedPath = scriptpath + '\\merged'
    if not os.path.exists(mergedPath): os.mkdir(mergedPath)
    if encrypt:
        cryptpath = os.path.join(partsPath,cryptfile)
        try:
            key = open(cryptpath, 'rb').read()
            print('Using existing encryption key \'' + cryptfile + '\'\n\n')
            fernet = Fernet(key)
        except:
            print("No crypto key found." + '\n')
    else:
        print("Encryption file not specified. Proceeding without encryption.")
    origName = re.sub('.part(.*)', '', filename)
    with open(os.path.join(mergedPath,origName),"wb") as out:
        for root, dirs, files in os.walk(filepath):
            parts = [file for file in files if origName + '.part' in file]
            i = 0
            while i < len(parts):
                part = [p for p in parts if p.endswith('.part' + str(i))]
                h = hashlib.md5()
                h.update(open(os.path.join(root,part[0]), 'rb').read())
                print(h.hexdigest() + spc + part[0])
                if encrypt: out.write(fernet.decrypt(open(os.path.join(root,part[0]),'rb').read()))
                else: out.write(open(os.path.join(root,part[0]),'rb').read())
                i = i + 1
    h = hashlib.md5()
    blockSize = 2**20
    with open(os.path.join(mergedPath,origName), 'rb') as f:
        while True:
            data = f.read(blockSize)
            if not data:
                break
            h.update(data)
    print('\n' + h.hexdigest() + spc + os.path.join(mergedPath,origName))
    

def fileSplit():
    global inputFile, mergedPath, partsPath, cryptfile
    chunksize = 1024 * (inputSize * 1000)
    print('Splitting operation started')
    h = hashlib.md5()
    blockSize = 2**20
    with open(inputFile, 'rb') as f:
        while True:
            data = f.read(blockSize)
            if not data:
                break
            h.update(data)
        origChecksum = h.hexdigest()
    out = origChecksum + spc + filename + '\n\n'
    print(out)
    logOutput.append(out)
    if not partsPath:
            print("Split folder not specified. Proceeding with default ./split/")
            partsPath = scriptpath + '\\split'
    if not os.path.exists(partsPath): os.mkdir(partsPath)
    if encrypt:
        if not os.path.exists(cryptfile):
            key = Fernet.generate_key()
            fernet = Fernet(key)
            print('Generating new encryption key ' + cryptfile + '\n')
            with open(cryptfile, 'wb') as keyfile: keyfile.write(key)
        else:
            key = open(cryptfile, 'rb').read()
            print('Using existing encryption key ' + cryptfile + '\n')
            fernet = Fernet(key)
    else:
        print("Encryption file not specified. Proceeding without encryption.")
    print("Splitting into " + str(inputSize) + " MB files")
    with open(inputFile,"rb") as file:
        num = 0
        while 1:
            chunk = file.read(chunksize)
            if not chunk: break
            if encrypt: chunk = fernet.encrypt(chunk)
            with open(os.path.join(partsPath,filename + '.part' + str(num)),"wb") as out: out.write(chunk)
            num = num + 1
    
    #Generate hashes after split
    for root, dirs, files in os.walk(partsPath):
        parts = [part for part in files if filename + '.part' in part]
        i = 0
        while i < len(parts):
            part = [p for p in parts if p.endswith('.part' + str(i))]
            h = hashlib.md5()
            h.update(open(os.path.join(root,part[0]), 'rb').read())
            out = h.hexdigest() + spc + part[0]
            print(out)
            logOutput.append(out + '\n')
            i = i + 1
    with open(os.path.join(partsPath,filename + '_checksums.log'),'w') as log:
        for line in logOutput: log.write(line)

def selectProcess():
    global inputFile
    if '.part' in inputFile: fileCombine()
    else: fileSplit()

def readOpts():
    global inputFile, filename, filepath, partsPath, mergedPath, cryptfile, encrypt, inputSize
    #Read input options   
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "e:s:m:f:c:")
    if opts:
        for opt, arg in opts:
            if opt in '-f':
                inputFile = arg
                if not os.path.exists(inputFile):
                    print("Specified file not found. Please check your specified path!")
                    sys.exit()
            elif opt in '-e':
                if '-' in arg or not arg:
                    print("Please specify a name for the keyfile using -e [path/filename]")
                    sys.exit()
                else:
                    encrypt = True
                    cryptfile = arg
            elif opt in '-s':
                partsPath = arg
            elif opt in '-m':
                mergedPath = arg
            elif opt in '-c':
                try:
                    inputSize = int(arg)
                except:
                    print("Please specify a split size in megabytes -c [number]")
        if inputFile:
            filename = os.path.basename(inputFile)
            filepath = os.path.dirname(inputFile)
            selectProcess()
        else:
            print("Input file not specified. Please specify an input file with -f [FILE]")
            sys.exit()
    else:
        print("""
SAM - Split and Merge by Magnus Heimonen, 2022

SAM splits large files into smaller parts or reassembles them, both with optional encryption and decryption. 

To process files, please use the following arguments:

-f [file]      Default: N/A
The file to process. This can be either an original file or a split. When merging, point to either of the ".part" files.

-e [file]      Default: N/A
This enables encryption on both splitting and merging. Specify a path and/or a name for the keyfile.

-s [folder]    Default: ./split/
The folder in which to place the split files and the checksums. This is only used when splitting.

-m [folder]    Default: ./merged/
The folder in which to place the merged file. This is only used when merging.

-c [number]    Default: 200
The size of the split files in Megabytes (MB)

        """)


 
readOpts()
