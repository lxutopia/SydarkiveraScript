import sys, os, hashlib, re, getopt
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from pathlib import Path
from cryptography.fernet import Fernet

scriptpath = os.path.abspath(sys.argv[0])
scriptpath = os.path.dirname(scriptpath)

mergedPath = scriptpath + '\\merged'
partsPath = scriptpath + '\\split'

filename = ''
filepath = ''
inputFile = ''
cryptfile = ''
inputSize = 200
logOutput = []
spc = '    '
encrypt = False
    
def textBoxUpdate(text):
    msg_label.insert('end',text)
    msg_label.update()
    msg_label.see(tk.END)

def fileCombine():
    global inputFile, inputSize, mergedPath, partsPath
    #If parts are specified, combine the parts
    print('\nMerging operation started\n')
    textBoxUpdate('\nMerging operation started\n')
    if not os.path.exists(mergedPath): os.mkdir(mergedPath)
    if encrypt:
        cryptpath = os.path.join(partsPath,cryptfile)
        try:
            key = open(cryptpath, 'rb').read()
            print('Using existing encryption key \'' + cryptfile + '\'\n\n')
            textBoxUpdate('Using existing encryption key \'' + cryptfile + '\'\n\n')
            fernet = Fernet(key)
        except:
            print("No crypto key found." + '\n')
            textBoxUpdate('No crypto key found.')
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
                textBoxUpdate(h.hexdigest() + spc + part[0] + '\n')
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
    textBoxUpdate('\n' + h.hexdigest() + spc + os.path.join(mergedPath,origName))
    textBoxUpdate('\n\nDone!')
    

def fileSplit():
    global inputFile, mergedPath, partsPath, cryptfile
    chunksize = 1024 * (inputSize * 1000)
    print('Splitting operation started')
    textBoxUpdate('Splitting operation started\n\n')
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
    textBoxUpdate(out)
    logOutput.append(out)
    if not os.path.exists(partsPath): os.mkdir(partsPath)
    if encrypt:
        if not os.path.exists(cryptfile):
            key = Fernet.generate_key()
            fernet = Fernet(key)
            print('Generating new encryption key ' + cryptfile + '\n')
            textBoxUpdate('Generating new encryption key \'' + cryptfile + '\'\n')
            with open(cryptfile, 'wb') as keyfile: keyfile.write(key)
        else:
            key = open(cryptfile, 'rb').read()
            print('Using existing encryption key ' + cryptfile + '\n')
            textBoxUpdate('Using existing encryption key \'' + cryptfile + '\'\n')
            fernet = Fernet(key)
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
            textBoxUpdate(out + '\n')
            logOutput.append(out + '\n')
            i = i + 1
    with open(os.path.join(partsPath,filename + '_checksums.log'),'w') as log:
        for line in logOutput: log.write(line)
    textBoxUpdate('\n\nDone!')

##GUI PART

def select_file():
    global inputFile, filename, filepath, partsPath, mergedPath
    f = fd.askopenfilename(title='Select File', initialdir=scriptpath)
    if f:
        inputFile = f
        if '.part' in inputFile:
            start_button['text'] = 'Merge'
            start_button['state'] = 'active'
            split_entry.delete(0, tk.END)
            split_entry.insert(0, os.path.dirname(inputFile))
            size_entry['state'] = 'disabled'
            encrypt_button['text'] = 'Decryption'
            if encrypt: encrypt_create_button['state'] = 'disabled'
            partsPath = os.path.dirname(inputFile)
        else:
            start_button['text'] = 'Split'
            start_button['state'] = 'active'
            size_entry['state'] = 'normal'
            encrypt_button['text'] = 'Encryption'
            if encrypt: encrypt_create_button['state'] = 'normal'
        file_entry.delete(0, tk.END)
        file_entry.insert(0, inputFile)  
        filename = os.path.basename(inputFile)
        filepath = os.path.dirname(inputFile)

def select_split_folder():
    global partsPath
    f = fd.askdirectory(title='Select File', initialdir=scriptpath)
    if f:
        partsPath = f
        split_entry.delete(0, tk.END)
        split_entry.insert(0, partsPath)
    
def select_merged_folder():
    global mergedPath
    f = fd.askdirectory(title='Select File', initialdir=scriptpath)
    if f:
        mergedPath = f
        merged_entry.delete(0, tk.END)
        merged_entry.insert(0, mergedPath)

def select_process():
    global cryptfile, inputFile, inputSize
    root.geometry("620x400")
    #Messagebox
    msg_label.grid(column=0 , row=8, sticky=tk.EW, padx=5, pady=5, columnspan=3)
    if inputFile:
        inputSize = int(guiSize.get())
        cryptfile = cryptname.get()
        if '.part' in inputFile: fileCombine()
        else: fileSplit()
    else:
        msg_label.insert('1.0','Please select a file to process.\n')

def set_encryption():
    global encrypt
    useEnc = useEncrypt.get()
    if useEnc == 'enc':
        encrypt = True
        encrypt_entry['state'] = 'normal'
        if '.part' not in inputFile: encrypt_create_button['state'] = 'normal'
        encrypt_open_button['state'] = 'normal'
    else:
        encrypt = False
        encrypt_entry['state'] = 'disabled'
        encrypt_create_button['state'] = 'disabled'
        encrypt_open_button['state'] = 'disabled'

def create_cryptfile():
    global cryptfile
    Files = [('All Files', '*.*'),
			('Key files', '*.key'),
			('Text Document', '*.txt')]
    f = fd.asksaveasfilename(filetypes = Files, title='Create keyfile', initialdir=scriptpath)
    if f:
        cryptfile = f
        encrypt_entry.delete(0, tk.END)
        encrypt_entry.insert(0, cryptfile)
    
def open_cryptfile():
    global cryptfile
    Files = [('All Files', '*.*'),
			('Key files', '*.key'),
			('Text Document', '*.txt')]
    f = fd.askopenfilename(filetypes = Files, title='Open keyfile', initialdir=scriptpath)
    if f:
        cryptfile = f
        encrypt_entry.delete(0, tk.END)
        encrypt_entry.insert(0, cryptfile)

def quitSoftware():
    sys.exit()

##Main
root = tk.Tk()
root.title('Sydarkivera SAM')
root.attributes('-topmost',True)
root.geometry("620x220")
root.resizable(True,False)
root.columnconfigure(0, weight=0)
root.columnconfigure(1, weight=2)

#Choose file
file_label = ttk.Label(root, text='File to process:')
file_label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

guiFile = tk.StringVar()
file_entry = ttk.Entry(root, textvariable=guiFile)
file_entry.grid(column=1, row=0, sticky=tk.EW, padx=5, pady=5)

file_button = ttk.Button(root,text="Select file",command=select_file)
file_button.grid(column=2, row=0, sticky=tk.E, padx=5, pady=5)

#Choose chunk size
size_label = ttk.Label(root, text='Size of splits:')
size_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

guiSize = tk.StringVar()
size_entry = ttk.Entry(root, textvariable=guiSize)
size_entry.insert(0, inputSize)
size_entry.grid(column=1, row=1, sticky=tk.E, padx=5, pady=5)

size_label_right = ttk.Label(root, text='MB')
size_label_right.grid(column=2, row=1, sticky=tk.W, padx=5, pady=5)

#Choose split folder
split_label = ttk.Label(root, text='Directory for split files:')
split_label.grid(column=0, row=4, sticky=tk.W, padx=5, pady=5)

split_entry = ttk.Entry(root, textvariable=partsPath)
split_entry.insert(0, partsPath)
split_entry.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5)

split_button = ttk.Button(root,text="Select folder",command=select_split_folder)
split_button.grid(column=2, row=4, sticky=tk.E, padx=5, pady=5)

#Choose merged folder
merged_label = ttk.Label(root, text='Directory for merged file:')
merged_label.grid(column=0, row=5, sticky=tk.W, padx=5, pady=5)

merged_entry = ttk.Entry(root, textvariable=mergedPath)
merged_entry.insert(0, mergedPath)
merged_entry.grid(column=1, row=5, sticky=tk.EW, padx=5, pady=5)

merged_button = ttk.Button(root,text="Select folder",command=select_merged_folder)
merged_button.grid(column=2, row=5, sticky=tk.E, padx=5, pady=5)

#Encryption
encrypt_frame = tk.Frame(root)
encrypt_frame.grid(column=0, row=6, sticky=tk.EW, padx=5, pady=5, columnspan=3)

useEncrypt = tk.StringVar()
encrypt_button = ttk.Checkbutton(encrypt_frame,text="Encryption", command=set_encryption, variable=useEncrypt, onvalue='enc', offvalue='noenc')
encrypt_button.pack(side=tk.LEFT)

encrypt_open_button = ttk.Button(encrypt_frame,text="Open",command=open_cryptfile, state='disabled')
encrypt_open_button.pack(side=tk.RIGHT)

encrypt_create_button = ttk.Button(encrypt_frame,text="Create",command=create_cryptfile, state='disabled')
encrypt_create_button.pack(side=tk.RIGHT)

cryptname = tk.StringVar()
encrypt_entry = ttk.Entry(encrypt_frame, textvariable=cryptname, state='disabled')
encrypt_entry.pack(side=tk.LEFT, fill='x', expand=1, padx=5, pady=5)

#Start/Cancel buttons
start_button = ttk.Button(root,text="Start",command=select_process, state='disabled')
start_button.grid(column=1 , row=7, sticky=tk.E, padx=5, pady=5)

cancel_button = ttk.Button(root,text="Close",command=quitSoftware)
cancel_button.grid(column=2 , row=7, sticky=tk.E, padx=5, pady=5)

credit_label = tk.Label(root, text='SAM by Magnus Heimonen', fg='#555')
credit_label.grid(column=0 , row=7, sticky=tk.W, padx=5, pady=5)

msg_label = tk.Text(root, height=10)
root.mainloop()