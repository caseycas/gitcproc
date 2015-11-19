
#get the path of directory in which project directories are there. Assume dirsPath

#rootdir ='C:\Users\Yagnik\PycharmProjects\Top_Project'
import re

import os
import sys
import ghProc
from logChunk import getExceptionKeyword


#print os.listdir(rootdir)
# for subdir, dirs, files in os.walk(rootdir):
#     print dirs

LOG_FILE="all_changed_log.txt"
pattern="\w*Exception"


def extractException(projPath):
    log_file = projPath + os.sep + LOG_FILE
    if not os.path.isfile(log_file):
        print("!! %s does not exist" % (log_file))
        return []
    #else:
        # print("Going to process %s " % (log_file))

    text=open(log_file,'r').read()
    all= re.findall(pattern,text)

    return all



def main():
  print "Utility to BULK process github logs"

  if len(sys.argv) < 2:
  	print "!!! Usage: python ExceptionExtractor.py top_project directory"
  	sys.exit()
  if not os.path.isdir("../Results"):
            os.mkdir("../Results")

  fPtrException=open("../Results/"+"ExceptionKeywords.txt",'w')




  rootdir = sys.argv[1]
  exceptionList=[]

  for dir in os.listdir(rootdir):
    path= os.path.join(rootdir,dir)
    # print path
    perProjectList=extractException(path)
    exceptionList.extend(perProjectList)


  for x in set(exceptionList):
      fPtrException.write(x+"\n")
  fPtrException.close()

if __name__ == '__main__':
  main()
