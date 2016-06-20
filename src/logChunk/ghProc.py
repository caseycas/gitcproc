'''This script takes one argument(the directory path in which the logfile is placed ).

For example, if the project is Android and the directory in which the android log file is placed is /home/username/Android.
The command to run the script on cli would be python ghProc.py /home/username/Android

The log file name is stored in LOG_FILE variable(by default all_log_nomerge_function.txt)'''


import sys
import os
import datetime
#from git import *

sys.path.append("../util")

import Util
from Util import ConfigInfo
from ghLogDb import ghLogDb
from getGitLog import LOG_FILE

#LOG_FILE = "all_changed_log_java.txt"

def dumpLog(projPath):

    log_file = projPath + os.sep + LOG_FILE

    if os.path.isfile(log_file):
        print("%s exists!!" % (log_file))
        return

    with Util.cd(projPath):

        logCmd = "git log --date=short -U1 -- \*.java > all_log.txt"
        print logCmd
        os.system(logCmd)

def processLog(projPath, c_info, password = ""):

    
    log_file = projPath + os.sep + LOG_FILE

    if not os.path.isfile(log_file):
        print("!! %s does not exist" % (log_file))
        return False
    else:
        print("Going to process %s " % (log_file))
    
    ghDb = ghLogDb(log_file, c_info, password)
    return ghDb.processLog()

def checkProj(project):

    if not os.path.isdir(project):
        print("!! %s does not exist" % (project))
        return False

    '''
    repo = Repo(project)
    if(repo.bare == False):
        print("!! %s is not a git repository" % (project))
        return False
    '''

    return True


'''main() funciton checks whether the arguments used while running the script are proper or not.'''

def main():
    print "Utility to process github logs"

    if len(sys.argv) < 3:
        print "!!! Usage: python ghProc.py project config_file [password]"
        sys.exit()

    project = str(sys.argv[1])
    config_file = sys.argv[2]
    config_info = ConfigInfo(config_file)   

    if(config_info.DATABASE):
        if(len(sys.argv) < 4):
            print("Database output selected, please input the password after the project")
            sys.exit()

        password = str(sys.argv[3])


    if checkProj(project) == False:
        print("!! Please provide a valid directory")
        return

    if(config_info.LOGTIME):
        start = datetime.datetime.now()

    #dumpLog(project)
    if(config_info.DATABASE):
        parseFinish = processLog(project, config_info, password)
    else:
        parseFinish = processLog(project, config_info)

    print "!! Done"

    if(config_info.LOGTIME):
        end = datetime.datetime.now()
        print("Project: " + project)
        print("Start time: " + str(start))
        print("Parse Finish time:" + str(parseFinish))
        print("End time: " + str(end))
        print("Parse time: " + str(parseFinish - start))
        print("Write time: " + str(end - parseFinish))
        print("Total time: " + str(end-start))


if __name__ == '__main__':
    main()








