[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://github.com/Recruit-CSIRT/MacRipper/blob/master/LICENSE)  

# MacRipper

Artifact analysis tool for macOS

<img src="imgs/macripper_cli_usage.gif" width="700">
<img src="imgs/macripper_gui_usage.gif" width="700">

## Abstract
`MacRipper` is a forensic tool for analyzing macOS artifacts.  
This tool is for macOS forensics beginners.  
The purpose is to make it easy to analyze.  
  
`MacRipper` has a GUI version and a CLI version, and can be used easily.  
Installation requires some libraries such as python3 and tcl-tk,  
You can easily install it by pasting the script below into the terminal and executing it.  
  
[macOSTriageTool](https://github.com/Recruit-CSIRT/macOSTriageTool) and other tools,  
Using macOS artifacts that preserve the directory structure as Input  
Output the result in .txt or .csv format.  
  
Works on macOS (verified by mojave and Catalina).  
  
## Features
- Offering GUI and CLI  
  - It has a GUI and is easy to use. Available according to use case and preference.  
 
- Easy function selection  
  - It has multiple analysis functions, and you can turn on / off the function by the check box.  

- Filtering by perspective of investigation  
  - Some modules output the results of filtering, such as `files brought in from outside` or` volume information of mounted`, from the viewpoint of investigation, to assist analysis.  
  - Refer to [User Guide](https://drive.google.com/open?id=1JAbcxza81T7xPfJl1HU5-CqmldAsoRTj) for details.  
    
## Installation
Execute the following script from the terminal.  
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Recruit-CSIRT/MacRipper/master/mac_ripper/install.sh)"
```

Depending on the installation environment, you may be required to enter a password in the middle. In that case,  
enter your password and press enter.  
  
When installation is completed, "MacRipper.app" is created under / Application /.  

If you cannot use MacRipper even if you use the installer script,  
install it using the following command.  
```
$ brew install python3
$ brew install tcl-tk
$ git clone https://github.com/Recruit-CSIRT/MacRipper.git; 
$ pip3 install --user -r MacRipper/mac_ripper/requirements.txt
$ mv MacRipper/mac_ripper/automator/MacRipper.app /Applications/MacRipper.app;
```

## Dependent module
 - python3  
 - tcl-tk
 - pytz  
 - lz4  
 - inquirer   
  
## Note
Due to the specification, it cannot be launched from Launchpad.  
Be sure to execute MacRipper.app from Finder.  
  
Make the following settings before use.  
- Terminal full disk access permission (for details, please refer to [User Guide](https://drive.google.com/open?id=1JAbcxza81T7xPfJl1HU5-CqmldAsoRTj))

## Quick start
There is a CLI version and a GUI version, which are used as shown below.

### CLI
For CLI, go to Contents/MacOS/ inside Macripper.app,
Execute mac_ripper_cli.py and parameters with sudo python3.
```
$ cd /Applications/MacRipper.app/Contents/MacOS/
$ sudo python3 mac_ripper_cli.py -r /Volumes/disk4s1/ -o ~/output/ -t Asia/Tokyo
```

### GUI
Click on MTT.app from the Finder and launch it.
Enter the setting items and press the "Rip It" button to start the analysis.

## How to use

### CLI
```
Usage of MacRipper:
 -h, --help show this help message and exit
  -r ROOT, --root ROOT please input evidence root path: e.g./Volumes/disk3s1/
  -o OUTPUT, --output OUTPUT
                        please input the output path.
  -t TIMEZONE, --timezone TIMEZONE
                        please input timezone for unifid log and spotlight module.:default Asia / Tokyo
  -c, --command spotlight module's option.parse store.db using Mac OS default command.
  -a, --all_files spotlight module's option.parse all files.
```
Also, after execution, a screen for selecting the execution module as shown below is displayed,
Select the module you want to execute and press Enter.
x is selected.
![gui](imgs/cli_option.png)

Example:
```
$ sudo python3 mac_ripper_cli.py -r /Volumes/disk4s1/ -o ~/output/ -t Asia/Tokyo
```

### GUI
<img src="imgs/gui.png" width="700">　

- Evidence root path: Specify root directory for analysis  
- Output path: Specify where to save the analysis results  
- Timezone(unifiedlog, spotlight):  
  - Select from pulldown  
  - Default is Asia/Tokyo  
- Options:  
  - Use all modules: Enable all options (except spotlight option)  
  - Use MRU module: Enables MRU artifact analysis module  
  - Use sqlite module: Enable sqlite analysis module  
  - Use unified log module: Enable unified log analysis module  
  - Use spotlight module: Enable spotlight analysis module  
    -- (Spotlight option) all fils: Get the spotlight meta information of all files  
    -- (Spotlight option) command: Get spotlight meta information using macOS mdls command (If you don't use this option, parse store.db to get information)  
    
### Tips
Refer to the following documents for details on how to use the tool, the function of each module, and how to read the output.
There are Japanese version and English version.
[User Guide](https://drive.google.com/open?id=1JAbcxza81T7xPfJl1HU5-CqmldAsoRTj)

In Catalina, if you use the host's  `/(route)` as input, please cut off SIP.
If SIP is enabled, spotlight module may not work.

## Third party software used internally
 - [spotlight_parser (ydkhatri)](https://github.com/ydkhatri/spotlight_parser)
 - [macMRU-Parser (mac4n6)](https://github.com/mac4n6/macMRU-Parser)
 - [hexdump.py (pypi)](https://pypi.python.org/pypi/hexdump)
 - [ccl_bplist.py (cclgroupltd)](https://github.com/cclgroupltd/ccl-bplist)
 - [mac_alias (pypi)](https://pypi.python.org/pypi/mac_alias)

## License
This repository is available under the GNU General Public License v3.0
  
## Author
kasasagi, stqp, moniik
