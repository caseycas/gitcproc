import sys
import os
import copy
from git import *


sys.path.append("../util")

import Util
import LanguageSwitcherFactory
from ghLogDb import ghLogDb
from dumpLogs import dumpLogs
from Config import Config



LOG_FILE = "all_log.txt"

def dumpLog(projPath, languages):

    if not os.path.isdir(projPath):
        print("!! Please provide a valid directory")
        return

    log_file = projPath + os.sep + LOG_FILE
 
    '''
    if os.path.isfile(log_file):
        print("%s exists!!" % (log_file))
        return
    '''
    extSet = LanguageSwitcherFactory.LanguageSwitcherFactory.getExtensions(languages)
    #print(extSet)
    all_extn = ""
    #for e in Util.cpp_extension:
    for e in extSet:
        all_extn += " \\*"  + e
        all_extn += " \\*"  + e.upper()
    with Util.cd(projPath):

        #TODO: Determine what log command is appropriate on a per language basis to provide sufficient context
        #but also minimize the amount of logs unnecessarily processed.
        #logCmd = "git log --date=short --no-merges -U1 -- " + all_extn + " > all_log.txt"
        #logCmd = "git log --date=short -U1000 --function-context -- " + all_extn + " > " + LOG_FILE
        #Assert Replication Command
        #Python and Java
        #logCmd = "git log --date=short --no-merges -U1 --function-context -- " + all_extn + " > " + LOG_FILE
        #C and C++ and Python
        if(".c" in extSet or ".cpp" in extSet or ".py" in extSet): 
            #This will still fail on really big files.... (could we see what the biggest file is and use that?)
            logCmd = "git log --date=short --no-merges -U99999 --function-context -- " + all_extn + " > " + LOG_FILE
        else: #Java
            logCmd = "git log --date=short --no-merges -U1 --function-context -- " + all_extn + " > " + LOG_FILE

        #os.system("git stash save --keep-index; git pull")
        print(logCmd)
        #Remove the old logs.
        try:
            os.system("rm " + LOG_FILE)
        except:
            print("Rm failed.")
            pass
        os.system(logCmd)



#This seems deprecated relative to ghProc.py
def processLog(projPath):

    if not os.path.isdir(projPath):
        print("!! Please provide a valid directory")
        return

    log_file = projPath + os.sep + LOG_FILE

    if not os.path.isfile(log_file):
        print("%s does not exist!!" % (log_file))
        return

    ghDb = ghLogDb(log_file)
    ghDb.processLog()


def getGitLog(project, languages):

    # dl = dumpLogs()
    # dl.cleanDb()

    projects = os.listdir(project)
    count = 0
    for p in projects:
        count += 1
        #if not p == 'gcc':
        #  continue
        proj_path = os.path.join(project, p)
        print proj_path
        dumpLog(proj_path, languages)
        #processLog(proj_path)


def main():
    print "==== Utility to process Github logs ==="

    if len(sys.argv) < 2:
        print "!!! Usage: python ghProc.py project [config_file]"
        sys.exit()

    project = sys.argv[1]
    config_file = Util.CONFIG
    if(len(sys.argv) == 3):
        config_file = sys.argv[2]

    cfg = Config(config_file)
    log_config = cfg.ConfigSectionMap("Log")
    try:
        langs = log_config['languages'].split(",")
    except:
        langs = [] #Treat empty as showing all supported languages.

    if not os.path.isdir(project):
        print("!! Please provide a valid directory")
        return

    getGitLog(project, langs)
    #processLog(project)
    print "Done!!"


if __name__ == '__main__':
    main()








