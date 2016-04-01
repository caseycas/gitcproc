import sys
import re
import csv
from collections import OrderedDict
from PatchMethod import PatchMethod

sys.path.append("../util")

import Util
import scopeTracker
import LanguageSwitcherFactory
import ScopeTrackerFactory
from dictUtil import incrementDict, nonZeroCount
from Config import Config
from chunkingConstants import *

#A log contains a raw set of text and a set of functions
#parsed from the text.
#TODO: Implement a mapping from language extensions to languages
class logChunk:
    def __init__(self, text = "", language = "C", config_file = Util.CONFIG):
        #Get the keyword file through the Config and .ini system
        cfg = Config(config_file)
        db_config = cfg.ConfigSectionMap("Keywords")
        self.KeyWordFile = db_config['file']

        self.text = text
        self.functions = []
        self.initialized = False
        self.total_add = 0
        self.total_del = 0
        self.header = "" #What is the name given after '@@' in log
        self.langSwitch = LanguageSwitcherFactory.LanguageSwitcherFactory.createLS(language)
        self.sT = ScopeTrackerFactory.ScopeTrackerFactory.createST(self.langSwitch)
        

    #list of strings --> boolean
    #Returns true if the string conforms to the pattern <keyword>,[included/excluded],[single,block]
    #and false otherwise
    def keywordValidityCheck(self, line):
        toCheck = [w.strip().lower() for w in line]
        if(len(toCheck) != 3):
            return False
        elif(toCheck[1] != INCLUDED and toCheck[1] != EXCLUDED):
            return False
        elif(toCheck[2] != SINGLE and toCheck[2] != BLOCK):
            return False
        else:
            return True

    def outputKeyword(self, kw):
        keyword = str(kw[0])
        if(keyword.startswith("\"") and keyword.endswith("\"")):
            return keyword[1:-1]
        else:
            return keyword


    #Read in a file with the following format:
    #Keyword, Inc/Exc, Single/Block 
    #And store them as a list of triples
    def readKeywords(self, lst):
        with open(self.KeyWordFile) as f:
            reader = csv.reader(f, delimiter=',', quotechar="\'")
            for l in reader:
                l = [w.lower() for w in l]
                if(self.keywordValidityCheck(l)):
                    next = l
                    lst.append(next)
                else:
                    print("Invalid line in keyword config file: " + str(l))
                    print("Skipping...")

        return lst

    def printLogChunk(self):
        print("===========================================")
        print("Total add: " + str(self.total_add))
        print("Total del: " + str(self.total_del))
        print("Header: " + str(self.header))
        print("Functions:")
        for func in self.functions:
            func.printFunc()
        print("===========================================")

    
    def setLang(self, language = "C"):
        self.langSwitch = LanguageSwitcherFactory.LanguageSwitcherFactory.createLS(language)
        self.sT = ScopeTrackerFactory.ScopeTrackerFactory.createST(self.langSwitch)


    #TODO: Not all variables refreshed + needs to be set for the correct set of variables.
    #Reset all the variables.
    def reset(self):
        self.text = ""
        self.functions = []
        self.initialized = False
        self.total_add = 0
        self.total_del = 0
        self.header = "" #What is the name given after '@@' in log
        self.sT = None
        self.langSwitch = None

    # -- -> Boolean
    #Return true if any function in this chunk has type MOCK
    def hasMockFunction(self):
        for func in self.functions:
            if(func.name == MOCK):
                #func.printFunc()
                return True

        return False

    # --> List of 2
    #Return a list of 2 element that show how many lines were added and removed from
    #the set of real functions in this chunk.
    def sumLinesForRealFunc(self):
        output = [0,0]
        for func in self.functions:
            if(func.name != MOCK):
                output[0] += func.total_add
                output[1] += func.total_del

        #This sum of the real function contents shouldn't be greater than
        #the total lines added and deleted in the diff.
        assert(output[0] <= self.total_add)
        assert(output[1] <= self.total_del)

        return output

    def functionCount(self):
        if(self.initialized == False):
            self.parseText()
        return len(self.functions)
        
    #string -> --
    #store the next line of the chunk in the text    
    def addToText(self, line):
        if(line.endswith("\n")):
            self.text += line
        else:
            self.text += line + "\n"

    #Remove any parts of the line that have structures marked as excluded
    def removeExcludedKeywords(self, line, keywords):
        excludedKeywords = [k for k in keywords if k[1] == EXCLUDED]
        line = line.lower() #Make this case insensitive
        for eK in excludedKeywords:
            # print(eK)
            line = line.replace(eK[0], "")
        return line
    
    #Determines if a line of text contains any keyword
    #Precondition - tested line has had all comments and strings removed.
    def containsKeyword(self, line, keywords):
        line = self.removeExcludedKeywords(line, keywords)
        includedKeywords = [k for k in keywords if k[1] == INCLUDED]
        for keyword in includedKeywords:
            if(keyword in line.lower()):
                return True

        return False

    #dictionary, list of tuples, list of strings -> dictionary
    #Update the add/delete for all open block contexts
    def incrementBlockContext(self, keywordDict, lineType, includedKeywords, blockContext):
        for b in blockContext:
            found = False
            for keyword in includedKeywords:
                if(b == keyword[0]):
                    assert(keyword[1] == INCLUDED and keyword[2] == BLOCK)
                    found = True
                    break

            if(not found):
                print("Invalid block keyword.")
                assert(False)

            if(lineType == ADD):
                incrementDict(str(b) + " Adds", keywordDict, 1)
            elif(lineType == REMOVE):
                incrementDict(str(b) + " Dels", keywordDict, 1)

        return keywordDict

    #String, String --> (String, Boolean)
    #If the keyword starts and ends with "", match segments not surrounded by alphanumeric keywords
    #Otherwise use basic "in"
    def keywordMatch(self, keyword, line):
        if(keyword.startswith('\"') and keyword.endswith('\"')):
            exactMatch = "(^|\W+)" + keyword[1:-1] + "(\W+|$)"
            return (keyword[1:-1],re.match(exactMatch, line) != None)
        else:
            return (keyword, keyword in line.lower())

    #String, String, list of Strings, dictionary, String -> dictionary
    #Modify the keyword dictionary for this line.  
    def parseLineForKeywords(self, line, lineType, keywords, keywordDict, blockContext = []):
        assert(lineType == ADD or lineType == REMOVE) #How do we handle block statements where only internal part modified?
        line = self.removeExcludedKeywords(line, keywords)
        #Make sure keywords are sorted by decreasing length, in case one is contained
        #inside the other, e.g. ut_ad and ut_a
        keywords = sorted(keywords, key=lambda tup: -len(tup[0]))
        if(Util.DEBUG):
            try:
                print("LINE TO PARSE FOR KEYWORD:" + line)
            except:
                print("LINE TO PARSE FOR KEYWORD:" + unicode(line, 'utf-8', errors='ignore'))
        includedKeywords = [k for k in keywords if k[1] == INCLUDED]
        tmp = line

        if(blockContext==[]):
            for keyword in includedKeywords:
                (k, matched) = self.keywordMatch(keyword[0], tmp)
                if(matched):
                    tmp = tmp.replace(k, "") #Then remove so we don't double count
                    if(lineType == ADD):
                        incrementDict(str(k) + " Adds", keywordDict, 1)
                    elif(lineType == REMOVE):
                        incrementDict(str(k) + " Dels", keywordDict, 1)
                    else: #I don't this case has been handled correctly for blocks.
                        print("Unmodified")
                        assert(0)

        elif(blockContext != []):
            #Sum over all block keywords
            keywordDict = self.incrementBlockContext(keywordDict, lineType, includedKeywords, blockContext)

        return keywordDict

    #String --> String
    #Given a line, return a pattern for a class declaration if the line ends
    #in a class declaration.  Otherwise, return ""
    def getClassPattern(self, line):
        temp = self.langSwitch.cleanClassLine(line)
        classPatterns = self.langSwitch.getClassRegexes()

        for c in classPatterns:
            result = re.search(c, temp)
            if(result != None):
                return result.group(0)

        return ""

    #Determine whether the given line is the begining of a class,
    #which can be confused with a function definition.
    #Should end with {
    def isClassDef(self, line):
        return (self.getClassPattern(line) != "")

    #Given a string of text that is a class name, extract the name of the class
    #I.e string is "class <name> ..."
    def extractClassName(self, line):
        components = line.split()
        #Remove endings of ":"
        if(components[1].endswith(":")):
            components[1] = components[1][:-1]
        elif(components[1].endswith("::")):
            components[1] = components[1][:-2]

        return components[1];

    #isConstructorOrDestructor: string, list
    #A variant of the constructor/ destructor check designed to simplify nesting issues
    #This requires less strict matching, but I find it difficult to think of non contrived
    #examples in the data where this will fail.
    def isConstructorOrDestructorWithList(self, line, classContextList):
        result = False
        for nextClass in classContextList:
            result = result or self.isConstructorOrDestructor(line, nextClass)
            if(result):
                return result

        return result

    #Given a string of text and a name of a surrounding class, decide if this is a constructor
    #or destructor for the class.
    def isConstructorOrDestructor(self, line, classContext):
        if(not self.langSwitch.isValidClassName(classContext)):
            return False

        temp = self.langSwitch.cleanConstructorOrDestructorLine(line)
        constructPatt = self.langSwitch.getConstructorOrDestructorRegex(classContext)

        if(Util.DEBUG == 1):
            print("Class context: " + classContext)
            try:
                print("Checking if a constructor/destructor: " + temp)
            except:
                print("Checking if a constructor/destructor: " + unicode(temp, 'utf-8', errors='ignore'))

        return re.search(constructPatt, temp,flags=re.IGNORECASE)

    def getBlockPattern(self,line,list):
        for l in list:
            l=str(l[0])
            result = re.search("\\b"+l+"\\b", line)
            if(result != None):
                #This is a hack to handle case where block keyword are used in single line. For eg. For loop without {} brackets.
                # TODO find a permanent solution of this.
                if("{" in line):
                    return result.group(0)

        return None

    #There are many structures that can be mistaken for a function.  We'll try to
    #ignore as many of them as possible.
    #To start, lets use a regex expression with "<return type> <name> (<0+ parameters>) {"
    #Also, we should handle template methods like: "template <class type> <return type> <name<type>>(<0+ parameters>) {""
    #Returns a string matching the function pattern or "" if no pattern match found.
    def getFunctionPattern(self, line): 
        #Remove potentially problematic structures
        temp = self.langSwitch.cleanFunctionLine(line)

        if(Util.DEBUG):
            try:
                print("Checking if function: \'" + temp + "\'")
            except:
                print("Checking if function: \'" + unicode(temp, 'utf-8', errors='ignore') + "\'")

        #Select patterns for our language and check against them
        funcPatterns = self.langSwitch.getFunctionRegexes()
        if(Util.DEBUG):
            print("Checking " + str(len(funcPatterns)) + " patterns.")

        for p in funcPatterns:
            result = re.search(p, temp)
            if(result != None):
                if(Util.DEBUG):
                    print("Found match with pattern: " + p)
                return result.group(0)


        return ""
            
    def isFunction(self, line):
        return (self.getFunctionPattern(line) != "")

    #Determine if the given line is an assignment block using the {
    def isAssignment(self, line):
        return re.search(assignPattern, line)        
                
    #String -> String
    #Given a line of code from a diff statement, return the line with any
    #string literals removed.
    def removeStrings(self, line):
        return self.langSwitch.removeStrings(line)
    
    #String, Boolean, String, String, String -> (String, String, Boolean, String, String)
    #Given a line of code from a diff statement, a marker if prior lines were a multiblock
    #comment, the marker for the type of line, a marker for the type of comment, and
    #the current running function name, and returns a 5-tuple containing
    #The modified line, the modified line type, the changed commentFlag, the commentType,
    #the running function name, and any changes if inside a function (this forces a continue)
    def removeComments(self, line, commentFlag, lineType, commentType, functionName, phase):
        #Thoughts: if inside block comment and we've added or deleted that line, it can be ignored
        #If it exists as code and has been commented out or added back in, it must have a corresponding line.
        #However, if inside a comment and the line is unmodified, we need to find if /* has been added or removed
        #When it is removed, we should consider the unmodified code as a block of added code.  When it is added
        #We should consider it as a block of deleted code.  (The /* and */ can be ignored, as if they contain code
        #They must also have a corresponding section of added or deleted code.)

        fChange = UNMARKED

        #Remove single line multi block comments...
        #line = re.sub(commentPattern, "", line)
        line = self.langSwitch.cleanSingleLineBlockComment(line)

        if(self.langSwitch.isBlockCommentStart(line)):
            commentFlag = True
            #We need to consider the content of the line before the /*
            line = self.langSwitch.beforeBlockCommentStart(line)
            commentType = lineType
            if(line.strip() == ""):
                if(phase == LOOKFOREND): #Make sure to count this line if inside function before continuing
                    if(lineType == ADD):
                        fChange = COMADD
                    elif(lineType == REMOVE):
                        fChange = COMDEL
                    else:
                        fChange = UNCHANGED
                else:
                    if(lineType == ADD):
                        fChange = TOTALADD
                    elif(lineType == REMOVE):
                        fChange = TOTALDEL
                    else:
                        fChange = UNCHANGED
                line = ""
        elif(self.langSwitch.isBlockCommentEnd(line)):
            if(commentFlag): #Normal case were whole /* ... */ comment is changed
                commentFlag = False
            elif(phase == LOOKFORNAME): #Case where only bottom part of comment is changed and looking for function name.
                functionName = "" #Clear the function name

            index = self.langSwitch.getBlockCommentEnd(line)
            if(len(line) > index + 2): #Case where there is code after comment end.
                line = line[index + 2:]
            else:
                if(phase == LOOKFOREND): #Make sure to count this line if inside function before continuing
                    if(lineType == ADD):
                        fChange = COMADD
                    elif(lineType == REMOVE):
                        fChange = COMDEL
                    else:
                        fChange = UNCHANGED
                else:
                    if(lineType == ADD):
                        fChange = TOTALADD
                    elif(lineType == REMOVE):
                        fChange = TOTALDEL
                    else:
                        fChange = UNCHANGED
                line = ""
        elif(commentFlag): #Inside a block comment
            if(lineType == ADD):
                line = ""
                if(phase == LOOKFOREND): #Make sure to count this line if inside function before continuing
                    fChange = COMADD
                else: #Otherwise, just add it to the total count of lines seen...
                    fChange = TOTALADD
            elif(lineType == REMOVE):
                line = ""
                if(phase == LOOKFOREND): #Make sure to count this line if inside function before continuing
                    fChange = COMDEL
                else:
                    fChange = TOTALDEL
            if(lineType == OTHER): #If the line is unmodified
                if(commentType == ADD): #This line has been commented out, with no corresponding block
                    lineType = REMOVE
                elif(commentType == REMOVE): #This line was commented out, but is now part of code again.
                    lineType = ADD
                else: #Unmodified line in an unmodified comment can be skipped
                    fChange = UNCHANGED
                    line = ""

        #Remove single line comments
        #line = re.sub(commentPattern2, "", line)
        line = self.langSwitch.cleanSingleLineComment(line)

        return (line,lineType, commentFlag, commentType, functionName, fChange)

    #If we have made changes to the comment structure, we want to count changes to the current
    #logChunk, function, and blocks separately so we can skip the rest of the changes.
    def modifyCountForComment(self, fChange, lineType, keywordDict, keywords, ftotal_add, ftotal_del):
        includedKeywords = [k for k in keywords if k[1] == INCLUDED]
        if(fChange == COMADD):
            if(self.sT.getBlockContext(lineType) != []):
                keywordDict = self.incrementBlockContext(keywordDict, lineType, includedKeywords, self.sT.getBlockContext(lineType))
            if(self.sT.getFuncContext(lineType) != []):
                ftotal_add += 1
            self.total_add += 1
        elif(fChange == COMDEL):
            if(self.sT.getBlockContext(lineType) != []):
                keywordDict = self.incrementBlockContext(keywordDict, lineType, includedKeywords, self.sT.getBlockContext(lineType))
            if(self.sT.getFuncContext(lineType) != []):
                ftotal_del += 1
            self.total_add += 1
        elif(fChange == TOTALADD):
            self.total_add += 1
        elif(fChange == TOTALDEL):
            self.total_del +=  1
        elif(fChange != UNCHANGED):
            assert("Not a valid fChange type.")

        return (keywordDict, ftotal_add, ftotal_del)

    #Update the counts of the total log chunk and function in the case of a normal, non comment
    #line.
    def updateCounts(self, lineType, ftotal_add, ftotal_del, phase, startFlag):
        if(lineType == ADD):
            self.total_add += 1 #This tracks + for whole chunks.
            if(phase == LOOKFOREND):
                if(startFlag==0):
                    ftotal_add += 1
        elif(lineType == REMOVE):
            self.total_del += 1
            if(phase == LOOKFOREND):
                if(startFlag==0):
                    ftotal_del += 1
        else:
            assert(lineType==OTHER)

        return (ftotal_add, ftotal_del)



    #String -> [lineType, String]
    #Given a line in the diff, return a list of 2 with the first line being ADD/REMOVE/OTHER and the second being
    #the line with the +/- removed, if applicable
    def markLine(self, line):
        if(line.startswith("+")):
            return [ADD, line[1:]]
        elif(line.startswith("-")):
            return [REMOVE, line[1:]]
        else:
            return [OTHER, line[0:]]
        

    #Main function to parse out the contents loaded into logChunk
    def parseText(self):

        '''
        Preprocess the log to swap the - } catch (*Exception) {
        and                            + } catch (#Exception) {
        '''

        #----------------------------------Initialization----------------------------------#

        #New keyword list for both single and block keywords.  This is a list of triples.
        keyWordList = []
        keyWordList = self.readKeywords(keyWordList)
        singleKeyWordList = filter(lambda w : w[2] == SINGLE, keyWordList)
        blockKeyWordList = filter(lambda w: w[2] == BLOCK, keyWordList)

        self.initialized = True
        lineNum = 0 # which line we are on, relative to the start of the chunk
        lineType = OTHER
        phase = LOOKFORNAME #TODO: Replace the phases with scopeTracker?
        commentFlag = False #Are we inside a comment?
        commentType = OTHER #Is the original line of the comment ADD, REMOVE, or OTHER
        functionName = ""
        shortFunctionName = ""
        funcStart = 0
        funcEnd = 0

        classContext = [] #If we are parsing inside a class, what is the closest class name?
        ftotal_add=0
        ftotal_del=0
        etotal_add=0 #TODO: From an earlier version, to be removed.
        etotal_del=0
        keywordDictionary = OrderedDict()
        outsideFuncKeywordDictionary = OrderedDict() # A grouping for all keywords found outside function contexts
        catchLineNumber=[]
        tryList=[]

        #Initialize keywords (This is repeated three times -> make into a subfunction)
        for keyword in singleKeyWordList:
            if(keyword[1] != EXCLUDED):
                keywordDictionary[self.outputKeyword(keyword)+ " Adds"]=0
                keywordDictionary[self.outputKeyword(keyword)+ " Dels"]=0
                #Currently only support single line keyword tracking outside of functions
                outsideFuncKeywordDictionary[self.outputKeyword(keyword) + " Adds"]=0
                outsideFuncKeywordDictionary[self.outputKeyword(keyword) + " Dels"]=0

        for keyword in blockKeyWordList:
            #Hack to make run with the 'tryDependentCatch' keyword
            if(not isinstance(keyword, list) or len(keyword) != KEYLISTSIZE):
                continue
            elif(keyword[1] != EXCLUDED):
                keywordDictionary[self.outputKeyword(keyword) + " Adds"]=0
                keywordDictionary[self.outputKeyword(keyword) + " Dels"]=0

        #----------------------------------Initialization----------------------------------#

        #Start of iteration over the lines.
        for line in self.text.split("\n"):
            startFlag=0
            lineNum += 1
            #Remove whitespace on ends.
            fullLine = line.strip()
                
            if(Util.DEBUG==1):
                try:
                    print("The real line: " + line)
                except:
                    print("The real line: " + unicode(line, 'utf-8', errors='ignore'))
            
            (lineType, line)= self.markLine(line)
            
            #Remove all strings from the line. (Get rid of weird cases of brackets
            #or comment values being excluded from the line.
            line = self.removeStrings(line)
            line = line.replace("\\", "") #Remove backslashes.
            line = line.replace("^M", "")
            
            #Remove all comments from the line
            fChange = UNMARKED
            (line, lineType, commentFlag, commentType, functionName, fChange) = self.removeComments(line, commentFlag, lineType, commentType, functionName, phase)

            #Update the all the counts if this is a comment line
            if(fChange != UNMARKED):
                (keywordDictionary, ftotal_add, ftotal_del) = self.modifyCountForComment(fChange, lineType, keywordDictionary, blockKeyWordList, ftotal_add, ftotal_del)
                continue
            else: #Otherwise, update just the function and total counts
                (ftotal_add, ftotal_del) = self.updateCounts(lineType, ftotal_add, ftotal_del, phase, startFlag)

            #Extract the name of the function
            if(phase == LOOKFORNAME):
                if(Util.DEBUG == 1):
                    try:
                        print("Current Name Search: " + functionName)
                    except:
                        print("Current Name Search: " + unicode(functionName, 'utf-8', errors='ignore'))

                #What if we've hit a function defintion?
                #TODO: Make language independent
                if(self.langSwitch.checkForFunctionReset(functionName)):
                    functionName = "" #Clear the name

                #Namespace problem comes in here. we add extra stuff in conjunction with functionName += ... above
                #How can we replace if and the { stuff below with scopeTracker methods? No, check for scope change
                if(self.sT.isScopeIncrease(line, lineType)):
                    if(Util.DEBUG == 1):
                        print("Scope increase while searching for function.")

                    if(self.sT.scopeIncreaseCount(line, lineType) > 1):
                        if(Util.DEBUG == 1):
                            print("Parsing of multiscope increases like: ")
                            print(line)
                            print("is not yet supported.")
                        continue

                    functionName = self.sT.appendFunctionEnding(line, functionName)

                    shortFunctionName = self.getFunctionPattern(functionName)
                    if(Util.DEBUG):
                        print("Pattern: " + shortFunctionName)


                    if(shortFunctionName != ""):
                        isFunction = True
                    elif((classContext != [] and self.isConstructorOrDestructorWithList(functionName, classContext))): #classContext becomes nonempty only for OO languages
                        isFunction = True
                        #Replace with general function.
                        shortFunctionName = self.langSwitch.shortenConstructorOrDestructor(functionName)
                    else:
                        isFunction = False

                    #Update to function scope or other here.
                    if(isFunction): #Skip things are aren't functions
                        if(Util.DEBUG == 1):
                            try:
                                 print("Function: " + shortFunctionName)
                            except:
                                 print("Function: " + unicode(shortFunctionName, 'utf-8', errors='ignore'))

                        self.sT.increaseScope(shortFunctionName, lineType, scopeTracker.FUNC)
                        funcStart = lineNum
                        phase = LOOKFOREND
                        #Count this line as an addition or deletion
                        #this means either a { will be counted or part
                        #of the function name. 
                        if(lineType == REMOVE):
                            ftotal_del = 1
                            startFlag=1
                        elif(lineType == ADD):
                            ftotal_add = 1
                            startFlag=1
                    else: #There was a non-function scope increase.
                        self.sT.increaseScope(line, lineType, scopeTracker.GENERIC)
                        if(self.langSwitch.isObjectOrientedLanguage()):
                            className = self.getClassPattern(functionName) #Would C++ constructors outside class A start with A::?
                            if(className != ""):
                                if(Util.DEBUG == 1):
                                    try:
                                        print("Class:" + className)
                                    except:
                                        print("Class:" + unicode(className, 'utf-8', errors='ignore'))
                                classContext.append(self.extractClassName(className)) #Push onto the class list
                            
                        functionName = "" #Reset name and find next
                else: #No scope change to cut off, so add the whole line instead
                    if(Util.DEBUG):
                        print("Extending the function name")
                    functionName += line.replace("\n", "") + " " #add the line with no new lines
                        
                #Check for single line keywords
                if(lineType != OTHER):
                    if(phase == LOOKFOREND):
                        keywordDictionary = self.parseLineForKeywords(line, lineType, singleKeyWordList, keywordDictionary)
                    elif(phase == LOOKFORNAME):
                        outsideFuncKeywordDictionary = self.parseLineForKeywords(line, lineType, singleKeyWordList, outsideFuncKeywordDictionary)
                    else:
                        assert(0)

                #Handle cases where we have a single line function.
                if(phase == LOOKFOREND and self.sT.isScopeDecrease(line, lineType)):
                    shortFunctionName = self.sT.getFuncContext(lineType) #Get the functional context
                    self.sT.decreaseScope(line, lineType)

                if(self.sT.getFuncContext(lineType) == "" and phase == LOOKFOREND):
                    funcEnd = lineNum

                    #Add this function to our list and reset the trackers.
                    #We use shortFunctionName, which is the string that matched our expected
                    #function pattern regex
                    funcToAdd = PatchMethod(self.langSwitch.parseFunctionName(shortFunctionName), funcStart, funcEnd, ftotal_add, ftotal_del,keywordDictionary,etotal_add,etotal_del,catchLineNumber)
                    
                    #Add assertions from current function
                    self.functions.append(funcToAdd)
              
                    #Reset asserts to current function
                    functionName = ""
                    shortFunctionName = ""
                    funcStart = 0
                    funcEnd = 0
                    ftotal_add = 0
                    ftotal_del = 0
                    etotal_add = 0
                    etotal_del = 0
                    phase = LOOKFORNAME
                    lineType=OTHER
                    for keyword in singleKeyWordList:
                        if(keyword[1] != EXCLUDED):
                            keywordDictionary[self.outputKeyword(keyword) + " Adds"]=0
                            keywordDictionary[self.outputKeyword(keyword) + " Dels"]=0
                    for keyword in blockKeyWordList:
                        #Hack to make run with the 'tryDependedCatch' keyword
                        if(not isinstance(keyword, list) or len(keyword) != KEYLISTSIZE):
                            continue
                        elif(keyword[1] != EXCLUDED):
                            keywordDictionary[self.outputKeyword(keyword) + " Adds"]=0
                            keywordDictionary[self.outputKeyword(keyword) + " Dels"]=0


                if(Util.DEBUG == 1):
                    print(classContext)

            elif(phase == LOOKFOREND): #determine the end of the function
                #Handle changes in scope
                scopeChanges = self.sT.scopeOrder(line, lineType)
                if(len(scopeChanges) > 2):
                    if(Util.DEBUG == 1):
                        print("Parsing of multiscope changes like: ")
                        print(line)
                        print("is not yet supported.")
                    continue

                else:
                    for nextScopeChange in scopeChanges:
                        if(nextScopeChange == INCREASE):
                            if(self.sT.isScopeIncrease(line, lineType)):
                                if(self.sT.scopeIncreaseCount(line, lineType) > 1):
                                    if(Util.DEBUG == 1):
                                        print("Parsing of multiscope increases like: ")
                                        print(line)
                                        print("is not yet supported.")
                                    continue

                                #if(phase2==LOOKFOREXCP):
                                foundBlock=self.getBlockPattern(line,blockKeyWordList)
                                if(foundBlock!=None):
                                    if(Util.DEBUG):
                                        print("Block start found: " + foundBlock)
                                    self.sT.increaseScope(foundBlock, lineType, scopeTracker.SBLOCK)
                                else:
                                    self.sT.increaseScope(line, lineType, scopeTracker.GENERIC)
                        else:
                            if(self.sT.isScopeDecrease(line, lineType)):
                                if(self.sT.getFuncContext(lineType) != ""): #Maybe?
                                    shortFunctionName = self.sT.getFuncContext(lineType) #Get the functional context
                                if(self.sT.getBlockContext(lineType) != [] and lineType!=OTHER):
                                    if(Util.DEBUG):
                                        print("Current block context: " + str(self.sT.getBlockContext(lineType)))
                                    keywordDictionary = self.parseLineForKeywords(line, lineType, blockKeyWordList, keywordDictionary, self.sT.getBlockContext(lineType))

                                self.sT.decreaseScope(line, lineType)


                #Problem: This misses the last line of a block context, and if we move it before, it will miss the first
                #How do we capture a line with multiple block contexts?
                if(lineType != OTHER):
                    if(phase == LOOKFOREND):
                        keywordDictionary = self.parseLineForKeywords(line, lineType, singleKeyWordList, keywordDictionary)
                        if(self.sT.getBlockContext(lineType) != []):
                            if(Util.DEBUG):
                                print("Current block context: " + str(self.sT.getBlockContext(lineType)))
                            keywordDictionary = self.parseLineForKeywords(line, lineType, blockKeyWordList, keywordDictionary, self.sT.getBlockContext(lineType))
                    else:
                        assert(0)

                
                if(self.sT.getFuncContext(lineType) == ""):
                    funcEnd = lineNum
                    #Add this function to our list and reset the trackers.
                    if(Util.DEBUG == 1):
                        print("OLD")
                        print(self.sT.oldVerStack)
                        print("NEW")
                        print(self.sT.newVerStack)
                        print(lineType)
                        print(shortFunctionName)
                        print(str(funcStart) + " : " + str(funcEnd))

                    funcToAdd = PatchMethod(self.langSwitch.parseFunctionName(shortFunctionName), funcStart, funcEnd, ftotal_add, ftotal_del,keywordDictionary,etotal_add,etotal_del,catchLineNumber)
                    
                    self.functions.append(funcToAdd)

                    #Reset asserts to current function
                    functionName = ""
                    shortFunctionName = ""
                    funcStart = 0
                    funcEnd = 0
                    ftotal_add=0
                    ftotal_del=0
                    etotal_add=0
                    etotal_del=0
                    phase = LOOKFORNAME
                    catchLineNumber=[]
                    foundBlock=""
                    #currentBlock=None
                    for keyword in singleKeyWordList:
                        if(keyword[1] != EXCLUDED):
                            keywordDictionary[self.outputKeyword(keyword) + " Adds"]=0
                            keywordDictionary[self.outputKeyword(keyword) + " Dels"]=0
                    for keyword in blockKeyWordList:
                        #Hack to make run with the 'tryDependedCatch' keyword
                        if(not isinstance(keyword, list) or len(keyword) != KEYLISTSIZE):
                            continue
                        elif(keyword[1] != EXCLUDED):
                            keywordDictionary[self.outputKeyword(keyword) + " Adds"]=0
                            keywordDictionary[self.outputKeyword(keyword) + " Dels"]=0


        #Suppose we have a function where only the top is modified,
        # e.g.
        # int renamedFunction(int arg1) {
        #   int x = 0;
        #Then we want to add this into the count even though there is a hanging }
        if(shortFunctionName != ""):
            #The end of the function will be said to be the cutoff of the change.
            funcEnd = lineNum
            funcToAdd = PatchMethod(self.langSwitch.parseFunctionName(shortFunctionName), funcStart, funcEnd, ftotal_add, ftotal_del,keywordDictionary,etotal_add,etotal_del,catchLineNumber)
            self.functions.append(funcToAdd)

        #Remove any unmodified functions
        self.functions = filter(lambda(x) : x.total_add != 0 or x.total_del != 0 , self.functions)

        #Clear out the scope.
        self.sT.clearScope()
        
        #Create a mock function for any asserts that do not fall into another function's list
        if nonZeroCount(outsideFuncKeywordDictionary):
            mockFunction = PatchMethod(MOCK, 0, 0, 0, 0, outsideFuncKeywordDictionary, 0, 0)
            self.functions.append(mockFunction)

        if(Util.DEBUG):
            print("Chunk End.")
     
        return self

