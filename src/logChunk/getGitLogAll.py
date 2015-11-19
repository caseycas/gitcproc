import sys
import os
import copy
from git import *

sys.path.append("../util")

import Util
from ghLogDb import ghLogDb
from dumpLogs import dumpLogs

LOG_FILE = "all_log.txt"

def dumpLog(projPath):

  if not os.path.isdir(projPath):
    print("!! Please provide a valid directory")
    return

  log_file = projPath + os.sep + LOG_FILE

  #if os.path.isfile(log_file):
  # 	print("%s exists!!" % (log_file))
  # 	return

  with Util.cd(projPath):

    repo = Repo('.')
    assert not repo.bare
  

    all_extn = ""
    for e in (Util.all_extension):
      all_extn += " \\*"  + e
      all_extn += " \\*"  + e.upper()

    #logCmd = "git log --date=short --no-merges -U1 -- " + all_extn + " > all_log.txt"
    logCmd = "git log --date=short -U10 " \
            + "--ignore-all-space --ignore-space-change "  \
            + "--diff-filter=M " \
            + "-- " + all_extn + " > all_log_diffs.txt"
            #+ "--function-context "

    os.system("git stash save --keep-index; git pull")
    #print(logCmd)
    os.system(logCmd)



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


def getGitLog(project):

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
    dumpLog(proj_path)
    #processLog(proj_path)


def main():
  print "==== Utility to process Github logs ==="

  if len(sys.argv) < 2:
  	print "!!! Usage: python ghProc.py project"
  	sys.exit()

  top_project = sys.argv[1]

  if not os.path.isdir(top_project):
    print("!! Please provide a valid directory")
    return

  projects = os.listdir(top_project)
  for p in projects:
    if p.startswith('top_'):
      project = top_project + os.sep + p
      getGitLog(project)
      #processLog(project)
  
  print "Done!!"


if __name__ == '__main__':
  main()








