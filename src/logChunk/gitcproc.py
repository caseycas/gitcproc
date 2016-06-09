import sys
import ghProc
import getGitLog
import subprocess
sys.path.append("../util")

import Util
from Util import ConfigInfo
'''
Gitcproc.py is the master script, it invokes:
1) The downloads from GitHub
2) Writes the commit logs out
3) Parses and writes the parse to the choosen output format
'''


if len(sys.argv) < 2:
        print "!!! Usage: python gitcproc.py config_file [password]"
        sys.exit()

config_file = sys.argv[1]
config_info = ConfigInfo(config_file)   

if(config_info.DATABASE):
    if(len(sys.argv) < 3):
        print("Database output selected, please input the password after the project")
        sys.exit()

    password = str(sys.argv[2])

#Create the output directory if it doesn't exist yet.

#Invoke the Java Downloads
subprocess.call([])

#Run GetGitLog

#Run ghProc

