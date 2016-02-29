import sys
import os
import codecs
import re
import csv
from logChunk import logChunk
from datetime import datetime, timedelta
sys.path.append("../util")

from dumpLogs import dumpLogs
from logChunk import logChunk
from PatchMethod import PatchMethod
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

    #Deprecated
    def addMethod(self, methodName):

        method = PatchMethod(methodName)
        self.methods.append(method)

    #LogChunk --> ---
    #Add the Log chunk's recorded methods to the Patch
    def addFunctions(self, nextLogChunk):
        self.methods += nextLogChunk.functions

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
        isExceptionPatch=toStr(self.isExceptionPatch)


        for m in self.methods:
            patchStr = (",").join((project, sha, language, fileName, isTest, isExceptionPatch, m.methodToCsv()))
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
        self.date       = None
        self.is_bug     = False
        self.log        = None
        self.patches    = []

    def __str__(self):

        return self.printSha()

    def dumpSha(self, dumpLogDb):

        project = toStr(self.project)
        sha     = toStr(self.sha)
        author  = toStr(self.author)
        commit_date = toStr(self.date)
        log     = toStr(self.log)
        is_bug  = toStr(self.is_bug)
        shaStr = (",").join((project,sha,author,commit_date,is_bug))

        dumpLogDb.dumpSummary(shaStr)

        self.dumpPatches(dumpLogDb)

    def dumpSummary(self, summaryStr):

        schema = self.db_config['schema']
        table = schema + "." + self.db_config['table_change_summary']

        sql_command = "INSERT INTO " + table + \
                      "(project, sha, author, commit_date, is_bug)" + \
                      "VALUES (" + summaryStr + ")"

    def shaToCsv(self,inf1,inf2,fPtrChangeSummary,fPtrPatchSummary):

        project = toStr(self.project).replace(","," ")
        sha     = toStr(self.sha)
        author  = toStr(self.author).replace(","," ")
        commit_date = toStr(self.date)
        log     = toStr(self.log)
        is_bug  = toStr(self.is_bug)


        shaStr = (",").join((project,sha,author,commit_date,is_bug))

        inf1.write(shaStr+"\n")
        fPtrChangeSummary.write(shaStr+"\n")
        self.patchesToCsv(inf2,fPtrPatchSummary)


    def printSha(self):

        retStr  = "------ Sha Details -----\n"
        retStr += "project     = %s\n" % (self.project)
        retStr += "sha         = %s\n" % (self.sha)
        retStr += "author      = %s\n" % (self.author)
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
        
        #This is hard coded and should be modified in the future.
        if(self.project == 'v8'):
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

    def __init__(self, logFile):

        self.log_file = logFile
        self.project_name = None
        self.curr_method = None
        self.cur_lang = None
        self.shas = []
    

    def __str__(self):

        print self.project_name
        for s in shas:
            print s

    def isSha(self,line):

        is_sha = re.search(SHA, line, re.IGNORECASE)
        sha = None
        if line.startswith("commit") and is_sha:
            sha = is_sha.group(0)
            if (Util.DEBUG == 1 or Util.DEBUGLITE == 1):
                print("COMMIT: " + sha)
        return sha

    def isAuthor(self,line,shaObj):

        assert(shaObj != None)
        is_auth = re.search(EMAIL, line, re.IGNORECASE)
        if line.startswith("Author:") and is_auth:
            author = is_auth.group(0)
            shaObj.author =  line.split(author)[0].split("Author:")[1]
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
                self.cur_lang = extension.split(".")[1]

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
            if Util.DEBUG == 1: 
                print("New @@: " + line)
                print("HEADER: " + curLogChunk.header)
            #Parse the previous chunk and store the results.
            if(curLogChunk.header != ""): #If there is an existing chunk to parse
                self.processLastChunk(patchObj, curLogChunk)
            if Util.DEBUG == 1:
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
    def processLastChunk(self, patchObj, curLogChunk):
        curLogChunk.parseText()
        patchObj.addFunctions(curLogChunk)


    def processLog(self, config = Util.CONFIG):

        project1 = os.path.split(self.log_file)[0]
        project1 = project1.rstrip(os.sep)
        self.project_name = os.path.basename(project1)
        print("---------- %s ------------\n" % (self.project_name))

        if(Util.DATABASE == 1):
            dl = dumpLogs()

        if(Util.CSV==1):
            if not os.path.isdir("../Results"):
                os.mkdir("../Results")
            inf1=open("../Results/"+str(self.project_name)+"ChangeSummary.csv",'w')
            fPtrChangeSummary=open("../Results/"+"ChangeSummary.csv",'a')

            inf1.write("project,sha,author,commit_date,is_bug\n")

            inf2=open("../Results/"+str(self.project_name)+"PatchSummary.csv",'w')
            fPtrPatchSummary=open("../Results/"+"PatchSummary.csv",'a')

            lst=[]
            listToDict={}
            mockChunk=logChunk("", "C")
            mockChunk.readKeywords(lst)
            keywords= [sub_list[0] for sub_list in lst]
            for keyword in keywords:
                listToDict[str(keyword)+" Adds"]=0
                listToDict[str(keyword)+" Dels"]=0

            inf2.write("project, sha, language, file_name, is_test,isExceptionPatch, method_name,total_add,total_del,%s\n"%",".join(listToDict.keys()))

        inf = codecs.open(self.log_file, "r", "iso-8859-1")

        shaObj   = None
        patchObj = None
        is_diff  = False
        log_mssg = ""
        is_no_prev_ver = False
        is_no_next_ver = False
        curLogChunk = logChunk("", "C", config)
        linenum = 0

        for l in inf:
            sha  = self.isSha(l)
            line = l

            if sha:
                if(shaObj != None):
                    if(Util.DATABASE):            
                        shaObj.dumpSha(dl)
                    else:
                        shaObj.printSha()
                        if(Util.CSV):
                            shaObj.shaToCsv(inf1,inf2,fPtrChangeSummary,fPtrPatchSummary)

                shaObj = Sha(self.project_name, sha)
                if(Util.DEBUGLITE): #Save for testing.
                    self.shas.append(shaObj) #This will become very memory intensive in large git logs.
                is_diff = False
                log_mssg = ""
                
                continue

            elif self.isAuthor(line,shaObj):
                continue

            elif self.isDate(line,shaObj):
                continue

            fullLine=line
            line=line.strip()

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
                            if Util.DEBUG == 1: 
                                print("New diff with previous version: " + line)
                                print("HEADER: " + curLogChunk.header)
                            self.processLastChunk(patchObj, curLogChunk)
                        
                        #Reset the current chunk obj
                        if Util.DEBUG == 1:
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
                            if Util.DEBUG == 1: 
                                print("New diff with no previous version: " + line)
                                print("HEADER: " + curLogChunk.header)
                            self.processLastChunk(patchObj, curLogChunk)

                            if Util.DEBUG == 1:
                                print("Resetting.")
                            curLogChunk.reset()
                            curLogChunk.setLang("." + self.cur_lang) #DOUBLE CHECK ME!

                    patchObj = self.createPatchWithNoPrevVersion(line)
                    shaObj.patches.append(patchObj)
                else: #Then we reached a content line.
                    self.processPatch(fullLine, patchObj, curLogChunk)


        #if shaObj != None:
        #    shaObj.patches.append(patchObj)


        #Make sure to get the last patch in the file!
        if(curLogChunk.header != ""): #If there is an existing chunk to parse
            if Util.DEBUG == 1: 
                print("Last Patch: " + line)
                print("HEADER: " + curLogChunk.header)
            self.processLastChunk(patchObj, curLogChunk)

        #Write out last sha.
        if(shaObj != None and Util.DATABASE):
            if(Util.DEBUGLITE):
                print("Writing to db.")
            shaObj.dumpSha(dl)

        if(Util.DATABASE == 1):
            print("Closing Time.")
            dl.close()
        
        if(Util.CSV == 1):
            shaObj.printSha();
            shaObj.shaToCsv(inf1,inf2,fPtrChangeSummary,fPtrPatchSummary)
            inf1.close()
            inf2.close()
            fPtrChangeSummary.close()
            fPtrPatchSummary.close()


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

