import sys
import os
import codecs
import re
import csv
import signal
from logChunk import logChunk
from datetime import datetime, timedelta
sys.path.append("../util")

from dumpLogs import dumpLogs
from Config import Config
from PatchMethod import PatchMethod
import TimeExceededError
from chunkingConstants import *
import Util

from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
SHA   = '[a-f0-9]{40}'
EMAIL = '<[\w.%/+-]+@([\w/.+-])+>'
DATE  = '[0-9]{4}-[0-9]{2}-[0-9]{2}'

lmtzr = WordNetLemmatizer()
stoplist = stopwords.words('english')

ERR_STR  = '\\berror\\b|\\bbug\\b|\\bfix\\b|\\bfixing\\b|\\bfixups\\b|\\bfixed\\b|\\bissue\\b|\\bmistake\\b|\\bblunder\\b|' \
            + '\\bincorrect\\b|\\bfault\\b|\\bdefect\\b|\\bflaw\\b|\\bglitch\\b|\\bgremlin\\b|\\btypo\\b|\\berroneous\\b'


def timeout(signum, frame):
    raise TimeExceededError.TimeExceededError("Timed Out")

def toStr(text):
    try:
        text1 = str(text).encode('iso-8859-1')
        temp_text = text1.replace("\'","\"")
        temp_text = temp_text.strip()
        return "\'" + str(temp_text) + "\'"
    except:
        print type(text)
        return "\'NA\'"

class Patch:

    def __init__(self, fileName, language):

        self.file_name = fileName
        self.language  = language

        self.is_test    = False
        self.methods  = []
        self.isExceptionPatch=False #TODO: Change

    def getFullTitleString(self):
        if(methods != []):
            return methods[0].getFullTitleString()
        else:
            return ""

    #Deprecated
    def addMethod(self, methodName):

        method = PatchMethod(methodName)
        self.methods.append(method)

    #LogChunk --> ---
    #Add the Log chunk's recorded methods to the Patch
    def addFunctions(self, nextLogChunk):
        self.methods += nextLogChunk.functions

    #Add another mock function for changes seen outside of a function.
    def addOutsideFunc(self, nextLogChunk):
        tmp = nextLogChunk.createOutsideFuncSummary()
        if(tmp != None):
            self.methods.append(tmp)

    def printPatch(self):

        retStr  = "\n\t------ Patch -----\n"
        retStr += "\tlanguage    = %s\n" % (self.language)
        retStr += "\tfile        = %s\n" % (self.file_name)
        retStr += "\tis_test     = %s\n" % (self.is_test)

        for m in self.methods:
            retStr += m.printPatch()

        return retStr


    def patchToCsv(self, sha, project, inf2,fPtrPatchSummary):

        sha      = toStr(sha)
        project  = toStr(project)
        language = toStr(self.language)
        fileName = toStr(self.file_name)
        isTest   = toStr(self.is_test)
        #isExceptionPatch=toStr(self.isExceptionPatch)


        for m in self.methods:
            # patchStr = (",").join((project, sha, language, fileName, isTest, isExceptionPatch, m.methodToCsv()))
            patchStr = (",").join((project, sha, language, fileName, isTest, m.methodToCsv()))
            inf2.write(patchStr+"\n")
            fPtrPatchSummary.write(patchStr+"\n")


    def dumpPatch(self, sha, project, dumpLog):

        sha      = toStr(sha)
        project  = toStr(project)
        language = toStr(self.language)
        fileName = toStr(self.file_name)
        isTest   = toStr(self.is_test)

        for m in self.methods:
            patchStr = (",").join((project, sha, language, fileName, isTest, m.dumpMethod()))
            dumpLog.dumpMethodChanges(patchStr, m.getTitleString())


class Sha:

    def __init__(self, project, sha):

        self.project    = project
        self.sha        = sha
        self.language   = None
        self.file_name  = None
        self.function   = None
        self.author     = None
        self.author_email = None
        self.date       = None
        self.is_bug     = False
        self.log        = None
        self.patches    = []

    def __str__(self):
        return self.printSha()

    def getFullTitleString(self):
        title = ""
        i = 0
        if(patches != []):
            #Iterate until we find a patch that contains a method.
            while(title == "" and i < len(patches)): 
                title = patches[i].getFullTitleString()
                i += 1

        return title

    def dumpSha(self, dumpLogDb):

        project = toStr(self.project)
        sha     = toStr(self.sha)
        author  = toStr(self.author)
        author_email = toStr(self.author_email)
        commit_date = toStr(self.date)
        log     = toStr(self.log)
        is_bug  = toStr(self.is_bug)
        shaStr = (",").join((project,sha,author,author_email,commit_date,is_bug))

        dumpLogDb.dumpSummary(shaStr)

        self.dumpPatches(dumpLogDb)

    def dumpSummary(self, summaryStr):

        schema = self.db_config['schema']
        table = schema + "." + self.db_config['table_change_summary']

        sql_command = "INSERT INTO " + table + \
                      "(project, sha, author, author_email, commit_date, is_bug)" + \
                      "VALUES (" + summaryStr + ")"

    def shaToCsv(self,inf1,inf2,fPtrChangeSummary,fPtrPatchSummary):

        project = toStr(self.project).replace(","," ")
        sha     = toStr(self.sha)
        author  = toStr(self.author).replace(","," ")
        author_email = toStr(self.author_email).replace(",", " ")
        commit_date = toStr(self.date)
        log     = toStr(self.log)
        is_bug  = toStr(self.is_bug)


        shaStr = (",").join((project,sha,author,author_email,commit_date,is_bug))

        inf1.write(shaStr+"\n")
        fPtrChangeSummary.write(shaStr+"\n")
        self.patchesToCsv(inf2,fPtrPatchSummary)


    def printSha(self):

        retStr  = "------ Sha Details -----\n"
        retStr += "project     = %s\n" % (self.project)
        retStr += "sha         = %s\n" % (self.sha)
        retStr += "author      = %s\n" % (self.author)
        retStr += "author_email= %s\n" % (self.author_email)
        retStr += "commit date = %s\n" % (self.date)
        retStr += "log         = %s\n" % (self.log)
        retStr += "is_bug      = %s\n" % (self.is_bug)

        retStr += self.printPatches()

        print retStr.encode('ascii', 'ignore')

    def dumpPatches(self,dumpLogDb):
        for p in self.patches:
            p.dumpPatch(self.sha, self.project, dumpLogDb)


    def patchesToCsv(self,inf2,fPtrPatchSummary):
        for p in self.patches:
            p.patchToCsv(self.sha, self.project, inf2,fPtrPatchSummary)


    def printPatches(self):

        retStr = ""
        for p in self.patches:
            retStr += p.printPatch()

        return retStr


    def if_bug(self, text):
        global ERR_STR
        global lmtzr
        global stoplist
        isBug = False
        
        text = text.lower()
        text = text.replace('error handl','')
        text = text.replace('error cod','')
        
        imp_words = [lmtzr.lemmatize(word) for word in text.lower().split() \
                        if ((word not in stoplist)) ]
        bug_desc = ' '.join([x for x in imp_words])
        
        if "bug= " in bug_desc or "bug=none" in bug_desc:
            return isBug
        
        if re.search(ERR_STR, '\b'+bug_desc+'\b', re.IGNORECASE):
            isBug = True

        return isBug

    def setLog(self, log):
            self.log = log
            if len(log) > 1000:
                self.log = log[:1000]

            self.is_bug = self.if_bug(log)


class ghLogDb:

    def __init__(self, logFile, c_info, password = ""):

        self.log_file = logFile
        self.project_name = None
        self.curr_method = None
        self.cur_lang = None
        self.shas = []
        self.dbPass = password
        self.config_info = c_info #configuration info and options

    

    def __str__(self):

        print self.project_name
        for s in shas:
            print s

    def isSha(self,line):

        is_sha = re.search(SHA, line, re.IGNORECASE)
        sha = None
        if line.startswith("commit") and is_sha:
            sha = is_sha.group(0)
            if (self.config_info.DEBUG or self.config_info.DEBUGLITE):
                print("COMMIT: " + sha)
        return sha

    def isAuthor(self,line,shaObj):

        assert(shaObj != None)
        is_auth = re.search(EMAIL, line, re.IGNORECASE)
        if line.startswith("Author:") and is_auth:
            author = is_auth.group(0)
            shaObj.author = line.split(author)[0].split("Author:")[1] 
            shaObj.author_email = author
            print("Email: "  + shaObj.author_email)
            shaObj.author = shaObj.author.strip()

            return True
        return False

    def isDate(self,line,shaObj):

        assert(shaObj != None)
        is_date = re.search(DATE, line, re.IGNORECASE)
        if line.startswith("Date:") and is_date:
            date = is_date.group(0)

            shaObj.date = date
            return True
        return False

    def createPatchWithNoPrevVersion(self, line):
        #there was no previous version of a file

        patchObj = None
        if line.startswith("index "):
            pass

        elif line.startswith("+++ b/"):

            file_name = line.split("+++ b/")[1]
            fileName, extension = os.path.splitext(file_name)

            if extension == "":
                self.cur_lang = ""
            else:
                self.cur_lang = extension.split(".")[1] #This is failing in 4e215131d2543a28a065c5161438c315316f9961 in git

            patchObj = Patch(file_name, self.cur_lang)

            if "test" in fileName:
                patchObj.is_test = True

        return patchObj

    def createPatch(self, line):

        patchObj = None
        if line.startswith("index "):
            pass

        elif line.startswith("--- a/"):

            file_name = line.split("--- a/")[1]
            fileName, extension = os.path.splitext(file_name)

            if extension == "":
                self.cur_lang = ""
            else:
                self.cur_lang = extension.split(".")[1]

            patchObj = Patch(file_name, self.cur_lang)

            if "test" in fileName:
                patchObj.is_test = True

        return patchObj

    def processPatch(self, line, patchObj, curLogChunk):

        if line.startswith("index "):
            pass

        elif line.startswith("--- a/"):
            assert(patchObj == None)
            file_name = line.split("--- a/")[1]
            fileName, extension = os.path.splitext(file_name)

            if extension == "":
                self.cur_lang = ""
            else:
                self.cur_lang = extension.split(".")[1]

            patchObj = Patch(file_name, self.cur_lang)

            if "test" in fileName:
                patchObj.is_test = True

        elif line.startswith("+++ b/"):
            pass

        elif line.startswith("@@ "):
            if(self.config_info.DEBUG): 
                print("New @@: " + line)
                print("HEADER: " + curLogChunk.header)
            #Parse the previous chunk and store the results.
            if(curLogChunk.header != ""): #If there is an existing chunk to parse
                self.processLastChunk(patchObj, curLogChunk)
            if(self.config_info.DEBUG):
                print("Resetting.")
            curLogChunk.reset()
            curLogChunk.setLang("." + self.cur_lang) #DOUBLE CHECK ME!

            temp_func   = line.split("@@ ")

            if len(temp_func) <= 2:
                method_name = "NA"
            else:
                temp_func = temp_func[-1]
                curLogChunk.addToText(temp_func.split(" ")[-1])
                if '(' in temp_func:
                    temp_func   = temp_func.rsplit('(')[0].strip()
                    method_name = temp_func.split(" ")[-1]
                else:
                    #not a traditional method, contains other signature
                    method_name = temp_func

            self.curr_method = method_name

            curLogChunk.header = method_name # Track this with our chunk obj

        else:
            curLogChunk.addToText(line) #Otherwise add the line to our separate parser

        return patchObj

    #When we come to the end of a log chunk, we need to parse it and verify what it
    #discovers against what git reports about the section of parsed text.  There are
    #several possible cases and all are handled below.  Modification of the error_cases
    #global marker should be limited to this method.
    #TODO: I think we should add an option to ignore extremely large commits.
    #E.g. there is a commit to ccv that adds all of sql lite 3.
    def processLastChunk(self, patchObj, curLogChunk):
        #print(patchObj.file_name) #Does just this hang the program for php-src.
        #Timeout idea thanks to Bogdan.
        #try:
        #    signal.alarm(30)
        curLogChunk.parseText()
        patchObj.addFunctions(curLogChunk)
        #I moved this to the end of parseTexts, wrap up.
        #patchObj.addOutsideFunc(curLogChunk)
            #Cancel the alarm signal.
        #    signal.alarm(0)
        #except TimeExceededError.TimeExceededError:
        #    print "Processing timed out. Skipping Chunk"


    def processLog(self, config = ""):
        if(config == ""):
            config = self.config_info.CONFIG

        signal.signal(signal.SIGALRM, timeout)

        project1 = os.path.split(self.log_file)[0]
        project1 = project1.rstrip(os.sep)
        self.project_name = os.path.basename(project1)
        print("---------- %s ------------\n" % (self.project_name))

        if(self.config_info.DATABASE):
            dl = dumpLogs(self.dbPass, self.config_info)

        if(self.config_info.CSV):
            if not os.path.isdir("../Results"):
                os.mkdir("../Results")
            inf1=open("../Results/"+str(self.project_name)+"ChangeSummary.csv",'w')
            fPtrChangeSummary=open("../Results/"+"ChangeSummary.csv",'w')

            inf1.write("project,sha,author,author_email,commit_date,is_bug\n")

            inf2=open("../Results/"+str(self.project_name)+"PatchSummary.csv",'w')
            fPtrPatchSummary=open("../Results/"+"PatchSummary.csv",'w')

            lst=[]
            listToDict={}
            mockChunk=logChunk("", "C", self.config_info) #TODO: This is C specific,  Why is this C specific?
            lst = mockChunk.readKeywords(lst)
            keywords= [k[0] for k in lst if k[1] == INCLUDED]
            for keyword in keywords:
                listToDict[str(keyword)+" Adds"]=0
                listToDict[str(keyword)+" Dels"]=0

            inf2.write("project, sha, language, file_name, is_test, method_name,total_add,total_del,%s\n"%",".join(sorted(listToDict.keys())))

        inf = codecs.open(self.log_file, "r", "iso-8859-1")

        shaObj   = None
        patchObj = None
        is_diff  = False
        log_mssg = ""
        is_no_prev_ver = False
        is_no_next_ver = False
        curLogChunk = logChunk("", "C", self.config_info)
        linenum = 0

        for l in inf:

            try:
                signal.alarm(0)

                sha  = self.isSha(l)
                line = l


                #if(self.config_info.DEBUGLITE):
                #    try:
                #        print(line)
                #    except:
                #        pass

                if sha:
                    #Reverting back to version that outputs at the end...
                    #if(shaObj != None):
                    #    if(self.config_info.DEBUGLITE):
                    #        print("Writing Sha:" + sha)

                    #    if(self.config_info.DATABASE):            
                    #        shaObj.dumpSha(dl)
                    #    elif(self.config_info.CSV):
                    #        shaObj.shaToCsv(inf1,inf2,fPtrChangeSummary,fPtrPatchSummary)
                    #    else:
                    #        shaObj.printSha()
          
                    shaObj = Sha(self.project_name, sha)
                    #if(self.config_info.DEBUGLITE): #Save for testing.
                    self.shas.append(shaObj) #This will become very memory intensive in large git logs.
                    
                    is_diff = False
                    log_mssg = ""
                    
                    continue

                elif self.isAuthor(line,shaObj):
                    continue

                elif self.isDate(line,shaObj):
                    continue

                fullLine=line
                line=line.rstrip()

                if line.startswith('diff --git '):
                    shaObj.setLog(log_mssg)
                    is_diff = True
                    is_no_prev_ver = False
                    is_no_next_ver = False
                    continue

                    if patchObj != None:
                        shaObj.patches.append(patchObj)

                elif is_diff == False:
                    if not line.strip():
                        continue
                    log_mssg += line + "\t"


                if is_diff:
                    if line.startswith("--- a/"):
                        #Finish the changes to the old patch object
                        if(patchObj != None):
                            #If there is an existing chunk to parse, process it
                            if(curLogChunk.header != ""):
                                if(self.config_info.DEBUG): 
                                    print("New diff with previous version: " + line)
                                    print("HEADER: " + curLogChunk.header)
                                self.processLastChunk(patchObj, curLogChunk)
                            
                            #Reset the current chunk obj
                            if (self.config_info.DEBUG):
                                print("Resetting.")
                            curLogChunk.reset()
                            curLogChunk.setLang("." + self.cur_lang) #DOUBLE CHECK ME!

                        patchObj = self.createPatch(line)
                        shaObj.patches.append(patchObj)
                        #print patchObj
                        #print shaObj.patches
                    elif (line == '--- /dev/null'): #earlier file was empty
                        is_no_prev_ver = True
                    elif (line == '+++ /dev/null'): #next file version was empty
                        is_no_next_ver = True
                        continue
                    elif (is_no_prev_ver == True) and line.startswith("+++ b/"):
                        #Finish the changes to the old patch object
                        if(patchObj != None):
                            if(curLogChunk.header != ""): #If there is an existing chunk
                                if (self.config_info.DEBUG): 
                                    print("New diff with no previous version: " + line)
                                    print("HEADER: " + curLogChunk.header)
                                self.processLastChunk(patchObj, curLogChunk)

                                if (self.config_info.DEBUG):
                                    print("Resetting.")
                                curLogChunk.reset()
                                curLogChunk.setLang("." + self.cur_lang) #DOUBLE CHECK ME!

                        patchObj = self.createPatchWithNoPrevVersion(line)
                        shaObj.patches.append(patchObj)
                    else: #Then we reached a content line.
                        self.processPatch(fullLine, patchObj, curLogChunk)

            except TimeExceededError.TimeExceededError:
                print("Line Timed out, moving to next.")
                continue

        #Clear timeouts.
        signal.alarm(0)

        #Make sure to get the last patch in the file!
        if(curLogChunk.header != ""): #If there is an existing chunk to parse
            if(self.config_info.DEBUG): 
                print("Last Patch: " + line)
                print("HEADER: " + curLogChunk.header)
            self.processLastChunk(patchObj, curLogChunk)

        #if shaObj != None:
        #    shaObj.patches.append(patchObj)

        parseFinish = datetime.now()

        if(self.shas != []): #If the log wasn't empty...
            #Create the change summary table and the method change table now if necessary
            if(self.config_info.DATABASE):
                cfg = Config(self.config_info.CONFIG)
                keywordFile = cfg.ConfigSectionMap("Keywords")
                full_title = dumpLogs.getFullTitleString(curLogChunk.getEmptyKeywordDict())

                dl.createSummaryTable()

                if(full_title != ""): #Check if the changes table exists and create it if we have a title.
                    dl.createMethodChangesTable(full_title)

            for s in self.shas:
                #s.printSha()
                if s != None:
                   if(self.config_info.DATABASE):            
                       s.dumpSha(dl)
                   elif(self.config_info.CSV):
                       s.shaToCsv(inf1,inf2,fPtrChangeSummary,fPtrPatchSummary)
                   else:
                       s.printSha()


        #Write out last sha.
        #if(shaObj != None and self.config_info.DATABASE):
        #    if(self.config_info.DEBUGLITE):
        #        print("Writing to db.")
        #    shaObj.dumpSha(dl)

        if(self.config_info.DATABASE):
            print("Closing Time.")
            dl.close()
        
        if(self.config_info.CSV):
            inf1.close()
            inf2.close()
            fPtrChangeSummary.close()
            fPtrPatchSummary.close()

        print("Sha's processed:")
        print(len(self.shas))

        return parseFinish


#---------test-----------#
def test():
    if len(sys.argv) < 2:
        print "!!! Pass a log file."
        print "usage ./ghLogDb.py ccv_all_log.txt"
        sys.exit()

    log_file = sys.argv[1]
    ghDb = ghLogDb(log_file)
    ghDb.processLog()


if __name__ == '__main__':
    test()


