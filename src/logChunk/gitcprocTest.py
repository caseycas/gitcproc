import sys
import unittest
import subprocess
import os
import csv
sys.path.append("../util")

import Util
from Util import ConfigInfo


class gitcprocTest(unittest.TestCase):
    '''
    This class is designed to run the tool end to end and make sure that
    the basic pipeline isn't broken.
    '''
    def setUp(self):
        self.config_file = "../util/gitcprocTest.ini"
        self.config_info = ConfigInfo(self.config_file)   
        self.repo_file = self.config_info.cfg.ConfigSectionMap("Repos")['repo_url_file']
        self.repos = [r.strip().replace("/", self.config_info.SEP) for r in open(self.repo_file, 'r')]
        #Get the download location
        self.output_loc = self.config_info.cfg.ConfigSectionMap("Repos")['repo_locations']

        #Get the log file names for this.
        self.log_files = [("../../evaluation/log_files/" + r + ".out", "../../evaluation/log_files/" + r + ".err") for r in self.repos]
        #Clean up old output and files for this
        for log in self.log_files:
            if(os.path.exists(log[0])):
                subprocess.call(["rm", log[0]])
            if(os.path.exists(log[1])):
                subprocess.call(["rm", log[1]])

        if(os.path.isdir("../../evaluation/repos/gitcprocTest/")):
            subprocess.call(["rm", "-rf", "../../evaluation/repos/gitcprocTest/"])
 
        subprocess.call(['mkdir', '-p', '../../evaluation/repos/gitcprocTest/'])

        self.csv_loc = "../Results/" + self.repos[0] + "ChangeSummary.csv" #Note that this is likely to change with better output configuration.
        self.csv_loc2 = "../Results/" + self.repos[0] + "PatchSummary.csv" #Note that this is likely to change with better output configuration.



    def testGitcproc(self):
        subprocess.call(["python", "gitcproc.py", "-d", "-wl", "-pl", self.config_file])

        
        self.assertTrue(len(self.repos) == 1)
        #Check that repo exists...
        self.assertTrue(os.path.exists(self.output_loc + "/" + self.repos[0]))
        #Check that git log file exists...
        self.assertTrue(os.path.exists(self.output_loc + "/" + self.repos[0] + "/all_log.txt"))

        #Check that log output exists and there are no errors in .err
        self.assertTrue(os.path.exists(self.log_files[0][0])) #Output
        self.assertTrue(os.path.exists(self.log_files[0][1])) #Error
        self.assertTrue(os.stat(self.log_files[0][1]).st_size == 0)

        #Check that csv files exist...
        #Get the csv location
        self.assertTrue(os.path.exists(self.csv_loc))
        self.assertTrue(os.path.exists(self.csv_loc2))

        #...And that they have expected output

        #CSV Loc (2 commits)
        csv_contents = []
        with open(self.csv_loc, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                csv_contents.append(row)

        self.assertTrue(len(csv_contents) == 3)

        csv_contents = []
        with open(self.csv_loc2, 'r') as f:
            reader = csv.reader(f, delimiter=',', quotechar='\'')
            for row in reader:
                csv_contents.append(row)

        #Csv Loc 2 (3 functions, 3 non functions, 1 print in each function)
        self.assertTrue(len(csv_contents) == 7)
        matched = 0 #Make sure these rows appear...
        for row in csv_contents:
            if(row[3] == "cppFile.cpp" and row[5] == "main"):
                print("C++ matched!")
                matched += 1
                self.assertTrue(int(row[6]) == 4)
                self.assertTrue(int(row[7]) == 0)
                self.assertTrue(int(row[8]) == 1)
                self.assertTrue(int(row[9]) == 0)
            elif(row[3] == "javaFile.java" and row[5] == "main"):
                print("Java matched!")
                matched += 1
                self.assertTrue(int(row[6]) == 3)
                self.assertTrue(int(row[7]) == 0)
                self.assertTrue(int(row[8]) == 1)
                self.assertTrue(int(row[9]) == 0)
            elif(row[3] == "pythonFile.py" and row[5] == "context"):
                print("Python matched!")
                matched += 1
                self.assertTrue(int(row[6]) == 2)
                self.assertTrue(int(row[7]) == 0)
                self.assertTrue(int(row[8]) == 1)
                self.assertTrue(int(row[9]) == 0)

        self.assertTrue(matched == 3)


if __name__=="__main__":
    unittest.main()
