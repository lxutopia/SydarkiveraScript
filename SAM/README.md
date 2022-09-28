<!--- State the text needed in the fields marked with [explanatory on what] if not needed remove the text. 
Feel free to use more mark down for formatting the text-->
# SAM - Split and Merge

## Explanation of the software
SAM (Split and Merge) is a software used to help our members prepare large backup packages for transfer.
The software can split files into smaller parts, merge them together again and offers AES-based encryption and decryption for each operation.

## Dependencies
This software is designed to run on all platforms and has been tested on Windows 10/11 and Ubuntu 20.10.

The software is distributed as an executable, pre-packaged with required libraries.
If you wish to run the non-compiled version, you will require the following Python 3 libraries:

- Hashlib
- Tkinter
- Cryptography

## How to use SAM GUI
1.  Place the software wherever you want, as long as the software has read/write privileges. We recommend placing it in the same folder as the files you wish to process.
2.	Run the software.
3.	Using the GUI, select the file you wish to process.
4.	If you are splitting a file, specify the size of the parts in Megabytes (MB). Depending on what file you have chosen, the software will recognise whether to split or merge the file.
6.	Specify the input and output folders accordingly. The software will update these dynamically when needed.
7.	If you want to use encryption/decryption, check the checkbox and choose to create or open a keyfile.
8.	Select Split or Merge to run the operation.

## How to use SAM CLI
Run the software through a terminal of your choice.

| Argument | Default value | Usage |  
|---------------|:-----------:|-----------|  
| -f [file] | N/A | Required. The file to process. This can be either an original file or a split. When merging, point to any ".part" created by SAM. |  
| -e [file] | N/A | Optional. Enables encryption/decryption on both splitting and merging. Specify a path and/or a name for the keyfile.  |
| -s [folder] | split | Optional. The folder in which to place the split files and the checksums. This is only used when splitting. |
| -m [folder] | merged | Optional. The folder in which to place the merged file. This is only used when merging. |
| -c [number] | 200 | Optional. The max size of the split files in Megabytes (MB) |

## Description by:
Magnus "PreAmbience" Heimonen, 2022-09-28
