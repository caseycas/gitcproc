import sys
import re
import csv
from collections import OrderedDict
from PatchMethod import PatchMethod

sys.path.append("../util")

import Util
from dictUtil import incrementDict, nonZeroCount
from Config import Config

#Constants for the keywords
SINGLE = "single"
BLOCK = "block"
INCLUDED = "included"
EXCLUDED = "excluded"

KEYLISTSIZE = 3

#Constants for which phase we are in
LOOKFORNAME = 1
LOOKFOREND = 2
LOOKFOREXCP=3
LOOKFOREXCPEND=4

#LineTypes
ADD = 1
REMOVE = 2
OTHER = 3

classPattern1 = " class [\w\d_: ]+ {$"
classPattern2 = "^class [\w\d_: ]+ {$"

#notClassPattern = "class.*;.*{"
validClassNamePattern = "[\w\d_:]+"

stringPattern = "\".*?\""
stringPattern2 = "\'.*?\'"

commentPattern = "/\*.*?\*/"
commentPattern2 = "//.*"
parenPattern = "\(.*?\)"
assignPattern = "= *{"
paramPattern = " *\([\w\d_,\[\]\*\(\)&: ]*\)[^;]*{" #What parameters to a call look like.

#Regex expressions for Java/C/C++ functions
functionPattern1 = " [\w\d:_]+&* *\** +[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
functionPattern2 = " [\w<>\d:_]+&* +\** *[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
functionPattern3 = " [\w\d:_]+&* *\** *[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) const *{$"
functionPattern4 = "^[\w\d:_]+&* *\** +[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
functionPattern5 = "^[\w<>\d:_]+&* +\** *[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
functionPattern6 = "^[\w\d:_]+&* *\** *[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) const *{$"
functionPattern7="[\w\d:_]+&* *\** *[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\)[\s]* throws [\w\W\s]+ *{$"
functionPattern8 = "^[\w\d:_]+&* *\** *[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\)[\s]* throws [\w\W\s]+ *{$"

anonymousClassPattern= "[\s\w\d_:~]+&* * = new [\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
namespacePattern = "namespace.*{" #namespaces can be not named.
externPattern = "extern *{"

#Regex expressions for C++ template functions
templatePattern1 = "template +< *class +.*> +[\w\d_]+ *\** +[\w\d_<>:~]+ *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
templatePattern2 = "template +< *class +.*> +[\w\d_]+ +\** *[\w\d_<>:~]+ *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
templatePattern3 = "template +< *typename +.*> +[\w\d_]+ *\** +[\w\d_<>:~]+ *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
templatePattern4 = "template +< *typename +.*> +[\w\d_]+ +\** *[\w\d_<>:~]+ *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
templatePattern5 = "template +< *DataType +.*> +[\w\d_]+ *\** +[\w\d_<>:~]+ *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
templatePattern6 = "template +< *DataType +.*> +[\w\d_]+ +\** *[\w\d_<>:~]+ *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"

catchModifyPattern="- *} *catch.*{\s*\+ *} *catch.*{\s*"

#Label for structures found outside of a function
MOCK = "NO_FUNC_CONTEXT"

#A text file for function that we know are asserts, but don't use
#the word assert in their names
otherAssertFile = "assertFunctions.txt"

#A log contains a raw set of text and a set of functions
#parsed from the text.
class logChunk:
    def __init__(self, text = "", config_file = Util.CONFIG):
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
        self.bracketMisMatch=0

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


    #Read in a file with the following format:
    #Keyword, Inc/Exc, Single/Block 
    #And store them as a list of triples
    def readKeywords(self, lst):
        with open(self.KeyWordFile) as f:
            reader = csv.reader(f, delimiter=',', quotechar="\"")
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

    #TODO: Not all variables refreshed + needs to be set for the correct set of variables.
    #Reset all the variables.
    def reset(self):
        self.text = ""
        self.functions = []
        self.initialized = False
        self.total_add = 0
        self.total_del = 0
        self.header = "" #What is the name given after '@@' in log

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

    #String, String, list of Strings, dictionary, String -> dictionary
    #Modify the keyword dictionary for this line.  
    def parseLineForKeywords(self, line, lineType, keywords, keywordDict, blockContext = None):
        assert(lineType == ADD or lineType == REMOVE) #How do we handle block statements where only internal part modified?
        line = self.removeExcludedKeywords(line, keywords)
        #Make sure keywords are sorted by decreasing length, in case one is contained
        #inside the other, e.g. ut_ad and ut_a
        keywords = sorted(keywords, key=lambda tup: -len(tup[0]))
        if(Util.DEBUG):
            print("LINE TO PARSE FOR KEYWORD:" + line.encode('utf-8'))
        includedKeywords = [k for k in keywords if k[1] == INCLUDED]

        if(blockContext==None):
            for keyword in includedKeywords:
                if(keyword[0] in line.lower()):
                    if(lineType == ADD):
                        incrementDict(str(keyword[0]) + " Adds", keywordDict, 1)
                    elif(lineType == REMOVE):
                        incrementDict(str(keyword[0]) + " Dels", keywordDict, 1)
                    else: #I don't this case has been handled correctly for blocks.
                        print("Unmodified")
                        assert(0)

        elif(blockContext != None):
            found = False
            for keyword in includedKeywords:
                if(blockContext == keyword[0]):
                    assert(keyword[1] == INCLUDED and keyword[2] == BLOCK)
                    found = True
                    break

            if(not found):
                print("Invalid block keyword.")
                assert(False)

            if(lineType == ADD):
                incrementDict(str(blockContext) + " Adds", keywordDict, 1)
            elif(lineType == REMOVE):
                incrementDict(str(blockContext) + " Dels", keywordDict, 1)


        return keywordDict

    #String -> String
    #Given a full function String: "<0-n other modifiers> <return_type> <name>(arg0, ..., argN) {"
    #Return <name> or "" if the string is not a function header
    def parseFunctionName(self, fullName):
        if(fullName.find("\n") != -1):
            fullName = fullName.replace("\n", "")

        multiline = fullName.split(";")
        name = multiline[len(multiline)-1]

        #print("Name: " + name)
        results = re.findall(parenPattern, name)
        #Since types can be of (), we want to find the index of the last and largest match to (.*)
        #Prefer largest, but if multiple equal size (i.e. returns a type with () and has no arguments)
        #get the later one.
        max = -1
        biggest = ""
        for r in results:
            if(Util.DEBUG == 1):
              print("Next: " + r)
            if(max <= len(r)):
                max = len(r)
                biggest = r

        
        if(biggest == ""):
            #raise ValueError("This line doesn't seem to be a function header", fullName)
            return "" #If not a function name - return nothing.

        #Get start index of last copy of biggest
        argStart = fullName.rfind(biggest)
        #print("ARGSTART: " + str(argStart))
        if(argStart == -1):
            raise ValueError("Regex said we found argument section, but now we can't find it.", fullName)

        #Break up the string prior to the () section
        pieces = fullName[0:argStart].split(" ")
        for next in reversed(pieces):
            if(next != ""):
                #print("Return: " + next.strip())
                return next.strip()

        raise ValueError("Couldn't find method name", fullName)

    def isExternBlock(self, line):
        return(re.search(externPattern, line.strip().lower().replace("\n", "")))

    #Determine if the line is a namespace
    def isNamespace(self, line):
        return re.search(namespacePattern, line.strip().lower().replace("\n", ""))

    #String --> String
    #Given a line, return a pattern for a class declaration if the line ends
    #in a class declaration.  Otherwise, return ""
    def getClassPattern(self, line):
        temp = line.strip().lower().replace("\n", "")
        result = re.search(classPattern1, temp)
        if(result != None):
            return result.group(0)
        result = re.search(classPattern2, temp)
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
        if("{" not in line):
            return False
        if(not re.search(validClassNamePattern, classContext)):
            return False

        temp = line.lower().strip().replace("~", "") #Just remove the "~" for destructors
        temp = temp.replace("\t", "")
        temp = temp.replace("\r", "")
        temp = temp.replace("\n", "")
        if(Util.DEBUG == 1):
            print("Class context: " + classContext)
            print("Checking if a constructor/destructor: " + line.encode('utf-8'))

        return re.search(classContext + paramPattern, temp)

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
        #Replace new lines and tabs
        temp = line.strip().replace("\n", "")
        temp = temp.replace("\t", "")
        temp = temp.replace("\r", "")
        #There is a weird case in hiphop-php where they included a arg1, arg2, "..."
        #Therefore, to handle this specific pseudo code case, I'm adding a special line to remove "..."
        temp = temp.replace("...", "")
        #Also, I will remove any instances of "const to deal with some tricky cases"
        temp = temp.replace(" const ", "")
        #And weird templates with no types
        temp = temp.replace("template<>", "")
        # Get rid of " : " case that caused problems in hiphop
        temp = temp.replace(" : ", "")
        # Get rid of visibility modifiers
        temp = temp.replace("public:", "")
        temp = temp.replace("private:", "")
        temp = temp.replace("protected:", "")
        #Sometimes an # ifdef, etc might appear in the middle of function args.  Purge them!
        if("ifdef" in temp and "#" in temp):
            temp = temp.replace("#", "")
            temp = temp.replace("ifdef", "")
        if("endif" in temp and "#" in temp):
            temp = temp.replace("#", "")
            temp = temp.replace("endif", "")
        if("ifndef" in temp and "#" in temp):
            temp = temp.replace("#", "")
            temp = temp.replace("ifndef", "")
        #Deal with if statements...
        temp = re.sub(" else", "", temp)
        temp = re.sub("^else", "", temp)
        temp = re.sub(" if", "", temp)
        temp = re.sub("^if", "", temp) 


        if(Util.DEBUG):
            print("Checking if function: " + line.encode('utf-8'))
        
        #Check for regular and template functions
        if("template" in temp):
            temp = temp.replace("static", "") #Quick fix.

            result = re.search(templatePattern1, temp)
            if(result != None):
                if(Util.DEBUG):
                    print("PATTERN T1")
                return result.group(0)
            result = re.search(templatePattern2, temp)
            if(result != None):
                if(Util.DEBUG):
                    print("PATTERN T@")
                return result.group(0)
            result = re.search(templatePattern3, temp)
            if(result != None):
                if(Util.DEBUG):
                    print("PATTERN T3")
                return result.group(0)
            result = re.search(templatePattern4, temp)
            if(result != None):
                if(Util.DEBUG):
                    print("PATTERN T4")
                return result.group(0)
            result = re.search(templatePattern5, temp)
            if(result != None):
                if(Util.DEBUG):
                    print("PATTERN T5")
                return result.group(0)
            result = re.search(templatePattern6, temp)
            if(result != None):
                if(Util.DEBUG):
                    print("PATTERN T6")
                return result.group(0)

            return ""
          
        else:
            result = re.search(anonymousClassPattern, temp)
            if(result!=None):
                if(Util.DEBUG):
                    print("ANONYMOUS CLASS!")
                return ""
            result = re.search(functionPattern1, temp)
            if(result != None):
                if(Util.DEBUG):
                    print("PATTERN 1")
                return result.group(0)
            result = re.search(functionPattern2, temp)
            if(result != None):
                if(Util.DEBUG):
                    print("PATTERN 2")
                return result.group(0)
            result = re.search(functionPattern3, temp)
            if(result != None):
                if(Util.DEBUG):
                    print("PATTERN 3")
                return result.group(0)
            result = re.search(functionPattern4, temp)
            if(result != None):
                if(Util.DEBUG):
                    print("PATTERN 4")
                return result.group(0)
            result = re.search(functionPattern5, temp)
            if(result != None):
                if(Util.DEBUG):
                    print("PATTERN 5")
                return result.group(0)
            result = re.search(functionPattern6, temp)
            if(result != None):
                if(Util.DEBUG):
                    print("PATTERN 6")
                return result.group(0)
            result = re.search(functionPattern7, temp)
            if(result != None):
                if(Util.DEBUG):
                    print("PATTERN 7")
                return result.group(0)
            result = re.search(functionPattern8, temp)
            if(result != None):
                if(Util.DEBUG):
                    print("PATTERN 8")
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
        line = re.sub(stringPattern, "", line)
        line = re.sub(stringPattern2, "", line)
        return line
    
    #TODO: This is a sub function replace the code segment from the main parseText.
    #It will need to be implemented in a future version as there are a few issues remaining.
    #String, Boolean -> String
    #Given a line of code from a diff statement, and a marker if prior lines were a multiblock
    #comment, return the line with any comments removed (on the fly comment removal)
    def removeComments(self, line, insideComment, lineType):
        #print("Next Line: " + line)
        if lineType!=REMOVE:

        #Ignore multiple line comments
            if(line.find("/*") != -1):
                commentFlag = True
                #We need to consider the content of the line before the /*
                line = line.split("/*")[0]
            elif(line.find("*/") != -1):
                if(commentFlag): #Normal case were whole /* ... */ comment is changed
                    commentFlag = False
                elif(phase == LOOKFORNAME): #Case where only bottom part of comment is changed and looking for function name.
                    functionName = "" #Clear the function name #TODO: Side effect to remove...

                index = line.find("*/")
                if(len(line) > index + 2): #Case where there is code after comment end.
                    line = line[index + 2:]
                else:
                    #continue
                    return
            elif(commentFlag):
                #continue
                return

        #Remove // comments from the string
        line = re.sub(commentPattern2, "", line)
    
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
        
    #TODO: This still needs to be abstracted better to be easier to understand and modify.
    #I'd like to revamp the bracket handling structure to better account for the different
    #needs of added, unmodified, and unchanged lines.
    def parseText(self):

        '''
        Preprocess the log to swap the - } catch (*Exception) {
        and                            + } catch (#Exception) {
        '''

        #New keyword list for both single and block keywords.  This is a list of triples.
        keyWordList = []
        keyWordList = self.readKeywords(keyWordList)
        singleKeyWordList = filter(lambda w : w[2] == SINGLE, keyWordList)
        blockKeyWordList = filter(lambda w: w[2] == BLOCK, keyWordList)

        # if self.isExceptionChunk(blockKeyWordList) !=None:
        #     self.isExceptionChunkFlag=True

        self.initialized = True
        lineNum = 0 # which line we are on, relative to the start of the chunk
        bracketDepth = 0
        self.bracketMisMatch=0
        lineType = OTHER
        phase = LOOKFORNAME
        phase2=LOOKFOREXCP
        commentFlag = False #Are we inside a comment?
        functionName = ""
        shortFunctionName = ""
        funcStart = 0
        funcEnd = 0
        nestingDepth = 0 # How many brackets should be open to say this function is closed?

        classContext = [] #If we are parsing inside a class, what is the closest class name?
        ftotal_add=0
        ftotal_del=0
        etotal_add=0 #TODO: From an earlier version, to be removed.
        etotal_del=0
        BlockBracketDepth=0
        keywordDictionary = OrderedDict()
        outsideFuncKeywordDictionary = OrderedDict() # A grouping for all keywords found outside function contexts
        catchLineNumber=[]
        tryList=[]
        currentBlock=None

        #Initialize keywords (This is repeated three times -> make into a subfunction)
        for keyword in singleKeyWordList:
            if(keyword[1] != EXCLUDED):
                keywordDictionary[str(keyword[0])+" Adds"]=0
                keywordDictionary[str(keyword[0])+" Dels"]=0
                #Currently only support single line keyword tracking outside of functions
                outsideFuncKeywordDictionary[str(keyword[0])+" Adds"]=0
                outsideFuncKeywordDictionary[str(keyword[0])+" Dels"]=0

        for keyword in blockKeyWordList:
            #Hack to make run with the 'tryDependentCatch' keyword
            if(not isinstance(keyword, list) or len(keyword) != KEYLISTSIZE):
                continue
            elif(keyword[1] != EXCLUDED):
                keywordDictionary[str(keyword[0])+" Adds"]=0
                keywordDictionary[str(keyword[0])+" Dels"]=0

        for line in self.text.split("\n"):
            startFlag=0
            lineNum += 1
            #Remove whitespace on ends.
            fullLine = line.strip()
            if not fullLine:
                continue
                
            if(Util.DEBUG==1):
                print("The real line: " + line.encode('utf-8'))
            
            marked = self.markLine(line)
            lineType = marked[0]
            line = marked[1]

            #line2 = line
            #line = fullLine
            
            #Remove all strings from the line. (Get rid of wierd cases of brackets
            #or comment values being excluded from the line.
            line = self.removeStrings(line)
            
            #Remove all comments from the line
            #TODO: ADD SUB Comment Removal Sub- FUNCTION

            #If there is a comment of the form /* .... */ (single line only) remove it.
            line = re.sub(commentPattern, "", line)

            #print("Next Line: " + line)
            if lineType!=REMOVE:

            #Ignore multiple line comments
                if(line.find("/*") != -1):
                    commentFlag = True
                    #We need to consider the content of the line before the /*
                    line = line.split("/*")[0]
                elif(line.find("*/") != -1):
                    if(commentFlag): #Normal case were whole /* ... */ comment is changed
                        commentFlag = False
                    elif(phase == LOOKFORNAME): #Case where only bottom part of comment is changed and looking for function name.
                        functionName = "" #Clear the function name

                    index = line.find("*/")
                    if(len(line) > index + 2): #Case where there is code after comment end.
                        line = line[index + 2:]
                    else:
                        if(phase == LOOKFOREND and lineType == ADD): #Make sure to count this line if inside function before continuing
                            ftotal_add += 1
                        continue
                elif(commentFlag):
                    if(phase == LOOKFOREND and lineType == ADD): #Make sure to count this line if inside function before continuing
                        ftotal_add += 1
                    continue

            #Remove // comments from the string
            line = re.sub(commentPattern2, "", line)

            if lineType!=REMOVE:
                self.bracketMisMatch+=(line.count("{") - line.count("}"))

            #print(str(bracketDepth) + ":" + str(nestingDepth))  


            #TODO: Convert into sub function to update the dictionaries
            if(lineType == ADD):
                self.total_add += 1 #This tracks + for whole chunks.
                #It is necessary for all the normal cases we had before
                #where the function context was correct.
                if(phase == LOOKFOREND):
                    if(startFlag==0):
                        ftotal_add += 1
            elif(lineType == REMOVE):
                self.total_del += 1
                if(phase == LOOKFOREND):
                    if(startFlag==0):
                        ftotal_del += 1
            else:
                lineType=OTHER



            #Extract the name of the function
            if(phase == LOOKFORNAME):
                #if(not line.startswith("-")):
                if lineType != REMOVE:
                    bracketDepth += line.count("{")

                if(Util.DEBUG == 1):
                    print("Current Name Search: " + functionName.encode('utf-8'))

                #What if we've hit a function defintion?
                if(line.strip().endswith(";")):
                    functionName = "" #Clear the name

                #Namespace problem comes in here. we add extra stuff in conjunction with functionName += ... above
                if(bracketDepth > nestingDepth):
                    #Add last line of name (everything before first "{")
                    if("{" in line):
                        functionName += line.split("{")[0] + "{"
                    else:
                        functionName += line.split("{")[0]

                    shortFunctionName = self.getFunctionPattern(functionName)
                    if(shortFunctionName != ""):
                        isFunction = True
                    elif((classContext != [] and self.isConstructorOrDestructorWithList(functionName, classContext))):
                        isFunction = True
                        shortFunctionName = functionName # don't do the shortening of the pattern for constructor/ destructor 
                        #This may be incorrect in general, but I'm just trying to get it to work on the examples I have.
                    else:
                        isFunction = False

                    if(isFunction): #Skip things are aren't functions
                        if(Util.DEBUG == 1):
                            print("Function: " + shortFunctionName.encode('utf-8'))
                        funcStart = lineNum
                        phase = LOOKFOREND
                        #Count this line as an addition or deletion
                        #this means either a { will be counted or part
                        #of the function name.  Its close enough to fair
                        #I think
                        #111415. YS. Total count was getting updated twice.
                        if(lineType == REMOVE):
                            ftotal_del = 1
                            startFlag=1
                        elif(lineType == ADD):
                            ftotal_add = 1
                            startFlag=1
                    else: #Something that looked like a function at first but wasn't
                        className = self.getClassPattern(functionName)
                        if(className != ""):
                            if(Util.DEBUG == 1):
                                print("Class:" + className.encode('utf-8'))
                            classContext.append(self.extractClassName(className)) #Push onto the class stack
                            nestingDepth += 1 #Functions are inside something now
                        elif(self.isNamespace(functionName)):
                            if(Util.DEBUG == 1):
                                print("Namespace:" + functionName.encode('utf-8'))
                            nestingDepth += 1 #Functions are inside something now
                        elif(self.isExternBlock(functionName)):
                            if(Util.DEBUG == 1):
                                print("Extern:" + functionName.encode('utf-8'))
                            nestingDepth +=1
                        else:
                            if(Util.DEBUG == 1):
                                print("Other type of bracket: " + functionName.encode('utf-8'))
                            nestingDepth +=1
                            
                        functionName = "" #Reset name and find next
                else: #No brackets to cut off, so add the whole line instead
                    functionName += line.replace("\n", "") + " " #add the line with no new lines
                        
                #Check for single line keywords
                if(lineType != OTHER):
                    if(phase == LOOKFOREND):
                        keywordDictionary = self.parseLineForKeywords(line, lineType, singleKeyWordList, keywordDictionary)
                    elif(phase == LOOKFORNAME):
                        outsideFuncKeywordDictionary = self.parseLineForKeywords(line, lineType, singleKeyWordList, outsideFuncKeywordDictionary)
                    else:
                        assert(0)

                #Handle case where we have body {} on same line.   
                #if(not line.startswith("-")):
                if lineType!=REMOVE:
                    bracketDepth -= line.count("}")
                if(bracketDepth == nestingDepth and phase == LOOKFOREND):
                    funcEnd = lineNum

                    #Add this function to our list and reset the trackers.
                    #We use shortFunctionName, which is the string that matched our expected
                    #function pattern regex
                    funcToAdd = PatchMethod(self.parseFunctionName(shortFunctionName), funcStart, funcEnd, ftotal_add, ftotal_del,keywordDictionary,etotal_add,etotal_del,catchLineNumber)
                    
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
                    phase2=LOOKFOREXCPEND
                    lineType=OTHER
                    for keyword in singleKeyWordList:
                        if(keyword[1] != EXCLUDED):
                            keywordDictionary[str(keyword[0])+" Adds"]=0
                            keywordDictionary[str(keyword[0])+" Dels"]=0
                    for keyword in blockKeyWordList:
                        #Hack to make run with the 'tryDependedCatch' keyword
                        if(not isinstance(keyword, list) or len(keyword) != KEYLISTSIZE):
                            continue
                        elif(keyword[1] != EXCLUDED):
                            keywordDictionary[str(keyword[0])+" Adds"]=0
                            keywordDictionary[str(keyword[0])+" Dels"]=0


                if(Util.DEBUG == 1):
                    print("Depths: " + str(bracketDepth) + ":" + str(nestingDepth))
                    print(classContext)

                #Set back the expected level for seeing the start of functions
                #Need to redo this so we stack everything?
                if(bracketDepth < nestingDepth):
                    if(Util.DEBUG == 1):
                        print("Adjusting depth.")
                        #print(classContext)
                    nestingDepth = bracketDepth

            elif(phase == LOOKFOREND): #determine the end of the function

                #if(not line.startswith("-")):
                if lineType!=REMOVE:
                    bracketDepth -= line.count("}")

                if(BlockBracketDepth>bracketDepth and phase2==LOOKFOREXCPEND):
                    phase2=LOOKFOREXCP
                    BlockBracketDepth=0

                if lineType!=REMOVE:
                    bracketDepth += line.count("{")


                if lineType!=REMOVE and phase2==LOOKFOREXCP:
                    foundBlock=self.getBlockPattern(line,blockKeyWordList)
                    if(foundBlock!=None):
                        phase2=LOOKFOREXCPEND
                        BlockBracketDepth=bracketDepth
                        currentBlock=foundBlock

                if(Util.DEBUG == 1):
                    print("End Check: " + str(bracketDepth))

                if(lineType != OTHER):
                    if(phase == LOOKFOREND):
                        keywordDictionary = self.parseLineForKeywords(line, lineType, singleKeyWordList, keywordDictionary)
                        if(phase2==LOOKFOREXCPEND and currentBlock!=None):
                            keywordDictionary = self.parseLineForKeywords(line, lineType, blockKeyWordList, keywordDictionary,currentBlock)
                    else:
                        assert(0)

                if(bracketDepth == nestingDepth):
                    funcEnd = lineNum
                    #Add this function to our list and reset the trackers.
                    if(Util.DEBUG == 1):
                      print(str(funcStart) + " : " + str(funcEnd))
                    funcToAdd = PatchMethod(self.parseFunctionName(shortFunctionName), funcStart, funcEnd, ftotal_add, ftotal_del,keywordDictionary,etotal_add,etotal_del,catchLineNumber)
                    
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
                    foundBlock={}
                    currentBlock=None
                    for keyword in singleKeyWordList:
                        if(keyword[1] != EXCLUDED):
                            keywordDictionary[str(keyword[0])+" Adds"]=0
                            keywordDictionary[str(keyword[0])+" Dels"]=0
                    for keyword in blockKeyWordList:
                        #Hack to make run with the 'tryDependedCatch' keyword
                        if(not isinstance(keyword, list) or len(keyword) != KEYLISTSIZE):
                            continue
                        elif(keyword[1] != EXCLUDED):
                            keywordDictionary[str(keyword[0])+" Adds"]=0
                            keywordDictionary[str(keyword[0])+" Dels"]=0


        #Suppose we have a function where only the top is modified,
        # e.g.
        # int renamedFunction(int arg1) {
        #   int x = 0;
        #Then we want to add this into the count.

        if(shortFunctionName != ""):
            #The end of the function will be said to be the cutoff of the change.
            funcEnd = lineNum
            funcToAdd = PatchMethod(self.parseFunctionName(shortFunctionName), funcStart, funcEnd, ftotal_add, ftotal_del,keywordDictionary,etotal_add,etotal_del,catchLineNumber)
            self.functions.append(funcToAdd)

        #Remove any unmodified functions
        self.functions = filter(lambda(x) : x.total_add != 0 or x.total_del != 0 , self.functions)
        
        #Create a mock function for any asserts that do not fall into another function's list
        if nonZeroCount(outsideFuncKeywordDictionary):
            mockFunction = PatchMethod(MOCK, 0, 0, 0, 0, outsideFuncKeywordDictionary, 0, 0)
            self.functions.append(mockFunction)

        if(Util.DEBUG):
            print("Chunk End.")
     
        return self

