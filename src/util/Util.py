import os
import sys
import os.path
import errno
import shutil

#Options flags
SEP = '__'
DEBUG = 0
DEBUGLITE = 1
DATABASE = 0
CSV=1
LOGTIME = 1
CONFIG = "../util/sample_conf.ini" #Location of the configuration file.

supportedLanguages = ["C", "C++", "Java"]

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)



#Generic create directory function
def create_dir(path):

    try:
        print path
        os.makedirs(path)
    
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    
def copy_dir(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: 
            raise

def cleanup(path):

    if os.path.isdir(path):
        print "!!! Cleaning up " , path
        shutil.rmtree(path)

        # var = raw_input("Path %s exists; do you want to delete it?" % (path))
        # print "you entered", var
        # if var.lower().startswith('y'):
        #   print "!!! Cleaning up " , path
        #   shutil.rmtree(path)
        
    elif os.path.isfile(path):
        print "!!! Removing " , path
        os.remove(path)

all_extension = ['.c', '.cc', '.cpp', '.c++', '.cp', '.cxx', '.h', '.ic', \
#                 '.cpp_' , '.cpp1' , '.cpp2' , '.cppclean' , \
#                 '.cpp_NvidiaAPI_sample' , '.cpp-s8inyu' , '.cpp-woains' , \
                 '.cs' , '.csharp' , '.m' , \
                 '.java' , '.scala' , '.scla' , \
                 '.go' , '.javascript' , '.js' , '.coffee' , '.coffeescript' , \
                 '.rb'  , '.php' , '.pl' ,  '.py' , \
                 '.cljx' , '.cljscm' , '.clj' , '.cljc' , '.cljs' , \
                 '.erl' , '.hs' ]

cpp_extension = [ '.c', '.cc', '.cpp', '.c++', '.cp', '.cxx', '.h', '.ic']
