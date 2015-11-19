#!/usr/bin/python

import sys, getopt
import os
import threading
import ntpath

import ghProc

CPP_PATH = 'projects' + os.sep + 'top_C++'
C_PATH = 'projects' + os.sep + 'top_C'

def processProject(projPath):
  """thread worker function"""

  print 'processProject : %s\n' % projPath 
  #print threading.current_thread().name
  ghProc.processLog(projPath)
  
  return

#threads = []
def processProjects(projList):
  
  for pj in projList:
    t = threading.Thread(target=processProject, name=ntpath.basename(pj), args=(pj,))
    #threads.append(t)
    t.start()

def findAll(root):
  proj_list = []

  for item in os.listdir(root):
    if os.path.isdir(os.path.join(root, item)):
      proj_list.append(item)

  return proj_list




def main(argv):
  inputfile = ''
  outputfile = ''
  c_projects = []
  cpp_projects = []
  
  try:
    opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
  except getopt.GetoptError:
    print 'runAll.py -i <inputfile> -o <outputfile>'
    sys.exit(2)

  if len(opts) == 0:
    #no argument is passed
    print 'runAll.py -i <inputfile> -o <outputfile>'
    sys.exit()

  for opt, arg in opts:
    if opt == '-h':
      print 'runAll.py -i <inputfile> -o <outputfile>'
      sys.exit()

    elif opt in ("-i", "--ifile"):
      inputfile = arg
    elif opt in ("-o", "--ofile"):
      outputfile = arg

  print 'Input file is :', inputfile
  print 'Output file is :', outputfile

  #populate arrays with c and c++ projects
  #cpp_projects = findAll(CPP_PATH)
  #c_projects = findAll(C_PATH)

  #print cpp_projects
  #print c_projects
  
  project_paths = []

  f = open(inputfile, 'r')
  
  orig_stdout = sys.stdout
  orig_stderr = sys.stderr
  for line in f:
    project_path = line.strip()
    if project_path.startswith('#'):
      continue

    # if project_name in cpp_projects:
    #   project_path = os.path.join(CPP_PATH, project_name)
    # elif project_name in c_projects:
    #   project_path = os.path.join(C_PATH, project_name)
    # else:
    #   project_path = ''
    sys.stdout = orig_stdout
    sys.stderr = orig_stderr
    print project_path
    
    #project_paths.append(project_path)
    project_name = ntpath.basename(project_path)
    sys.stdout = open(project_name + '.out', 'w')
    sys.stderr = open(project_name + '.err', 'w')
    print project_path
    ghProc.processLog(project_path)

  f.close()

  #processProjects(project_paths)

if __name__ == "__main__":
  main(sys.argv[1:])
