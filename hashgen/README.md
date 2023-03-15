<!--- State the text needed in the fields marked with [explanatory on what] if not needed remove the text. 
Feel free to use more mark down for formatting the text-->
# Hashgen

## Explanation of the software
Hashgen is used for file validation through MD5 hashes.
The software generates a registry of hashes based on user search parameters.
On consecutive runs, the software validates the existing files against those in the registry, detecting changes such as new or removed files.
Hashgen automatically generates logs for each run.

## Dependencies
This software is designed to run on all platforms and has been tested on Windows 10/11 and Ubuntu CentOS 7.
Hashgen is written in Python 2 to allow it to run on older Linux distributions without additional downloads.

## How to run the software
1.  Place hashgen.py in its own folder.
2.	Run a terminal.
3.	Run the software with ```python hashgen.py```

```
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
    Help. Shows the manual.
```

## Description by:
Magnus "PreAmbience" Heimonen, 2022-04-12
