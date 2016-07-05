import sys
import os
import copy
from git import *


sys.path.append("../util")

import Util
import LanguageSwitcherFactory
from ghLogDb import ghLogDb
from Config import Config
from Util import ConfigInfo


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
        #I think there are some problems here that are making us trace some unnecessary changes:
        #I'm going to list some of the optional commands that I think may be relevant (b/c I'm seeing)
        #cases were we measure commits that seem to just be file renames or moves, and I think this is
        #adding a significant amount of additional work.  Also, why are we ignoring merge commits?

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


def getGitLog(project, languages, config_info):
    #Get the which subset of projects to run on.
    repo_config = config_info.cfg.ConfigSectionMap("Repos")
    project_set = set()
    
    '''
    Iterate over the projects to write the file for.
    '''
    try:
        with open(repo_config['repo_url_file'], 'r') as f:
            for line in f:
                project_set.add(line.strip().replace("/", config_info.SEP))
    except:
        if(config_info.DEBUG or config_info.DEBUGLITE):
            print("Error reading in the project list file, writing logs to all projects.")


    projects = os.listdir(project)
    if(len(project_set) == 0):
        project_set = projects

    for p in projects:
        print(p)
        if(p not in project_set): # User has specified only a subset of the downloaded projects should be processed for logs
            continue
        proj_path = os.path.join(project, p)
        if(config_info.DEBUGLITE or config_info.DEBUG):
            print proj_path
        dumpLog(proj_path, languages)
        #processLog(proj_path)


def main():
    print "==== Utility to process Github logs ==="

    if len(sys.argv) < 3:
        print "!!! Usage: python ghProc.py project config_file"
        sys.exit()

    project = sys.argv[1]
    config_file = sys.argv[2]      


    config_info = ConfigInfo(config_file)  
    log_config = config_info.cfg.ConfigSectionMap("Log")
    try:
        langs = log_config['languages'].split(",")
    except:
        langs = [] #Treat empty as showing all supported languages.

    if not os.path.isdir(project):
        print("!! Please provide a valid directory")
        return

    getGitLog(project, langs, config_info)
    #processLog(project)
    print "Done!!"


if __name__ == '__main__':
    main()








