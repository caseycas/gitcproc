import sys
import re
from PatchMethod import PatchMethod
import codecs

sys.path.append("../util")

import Util


#This is harder than I thought.  Problem is that the function names can span
#multiple lines and include additions and deletions.

#So, in the case of an NA, we likely need to create a new object to hold the whole string
#up to the next chunk.
#Then divide up for each method in chunk and create separate row for that.

#A function has a name, a start line, and an ending line


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

stringPattern = "\".*\""
commentPattern = "/\*.*\*/"
commentPattern2 = "//.*"
parenPattern = "\(.*\)"
assignPattern = "= *{"
paramPattern = " *\([\w\d_,\[\]\*\(\)&: ]*\)[^;]*{" #What parameters to a call look like.
functionPattern1 = " [\w\d:_]+&* *\** +[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
functionPattern2 = " [\w\d:_]+&* +\** *[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
functionPattern3 = " [\w\d:_]+&* *\** *[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) const *{$"
functionPattern4 = "^[\w\d:_]+&* *\** +[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
functionPattern5 = "^[\w\d:_]+&* +\** *[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
functionPattern6 = "^[\w\d:_]+&* *\** *[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) const *{$"
functionPattern7 = " [\w\d:_]+&* *\** *[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) throws \w+ *{$"
functionPattern8 = "^[\w\d:_]+&* *\** *[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) throws \w+ *{$"



namespacePattern = "namespace.*{" #namespaces can be not named.
externPattern = "extern *{"

templatePattern1 = "template +< *class +.*> +[\w\d_]+ *\** +[\w\d_<>:~]+ *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
templatePattern2 = "template +< *class +.*> +[\w\d_]+ +\** *[\w\d_<>:~]+ *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
templatePattern3 = "template +< *typename +.*> +[\w\d_]+ *\** +[\w\d_<>:~]+ *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
templatePattern4 = "template +< *typename +.*> +[\w\d_]+ +\** *[\w\d_<>:~]+ *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
templatePattern5 = "template +< *DataType +.*> +[\w\d_]+ *\** +[\w\d_<>:~]+ *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
templatePattern6 = "template +< *DataType +.*> +[\w\d_]+ +\** *[\w\d_<>:~]+ *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"

MOCK = "Mock_Function_For_Asserts"

#A text file for function that we know are asserts, but don't use
#the word assert in their names
otherAssertFile = "assertFunctions.txt"

class functionObj:

    def __init__(self, name, start=0, end=0, added=0, deleted=0,exception_add=0,exception_del=0,excepDict={}):
        self.name = name
        self.start = start
        self.end = end
        self.assertionList = [] #List of triples - line #, line type, actual assert
        self.total_add = added
        self.total_del = deleted
        self.total_excep_add=exception_add
        self.total_excep_del= exception_del
        self.excepDict =excepDict

    #int, int, string -> ---
    #Add an assertion to the list, taking a line number, ADD/REMOVE/OTHER, and
    #the text of the assertion
    def addAssertion(self, lineNum, modType, assertText):
        self.assertionList.append((lineNum, modType, assertText))

    #Return this object as a PatchMethod
    def convertToPatchMethod(self):
        converted = PatchMethod(self.name)
        converted.total_add = self.total_add
        converted.total_del = self.total_del
        for nextAssert in self.assertionList:

            if(nextAssert[1]==ADD):
                converted.assert_add += 1
                if(self.name==MOCK):
                    converted.total_add += 1
            elif(nextAssert[1]==REMOVE):
                converted.assert_del += 1
                if(self.name==MOCK):
                    converted.total_del += 1

        return converted

    def printFunc(self):
        print("===========================================")
        print(self.name)
        print(self.start)
        print(self.end)
        print(self.total_add)
        print(self.total_del)
        print(self.assertionList)
        print("===========================================")


#A log contains a raw set of text and a set of functions
#parsed from the text.
# def __init__(self, text = ""):
# self.text = text
# self.initialized = False
# self.total_add = 0
# self.total_del = 0
# self.otherAssertTypes = self.readKnownTypes()
# self.header = "" #What is the name given after '@@' in log

def printLogChunk(self):
    print("===========================================")
    print("Total add: " + str(self.total_add))
    print("Total del: " + str(self.total_del))
    print("Header: " + str(self.header))
    print("Functions:")
    for func in self.functions:
        func.printFunc()
    print("===========================================")

#Reset all the variables.
def reset(self):
    self.text = ""
    self.functions = []
    self.initialized = False
    self.total_add = 0
    self.total_del = 0
    self.otherAssertTypes = self.readKnownTypes()
    self.header = "" #What is the name given after '@@' in log


#Read in the set of functions that are known to be asserts but aren't
#named as expected.
def readKnownTypes(self):
    temp = []
    with open(otherAssertFile) as f:
        for line in f:
            temp.append(line.strip()) #remove new lines and space
    return temp

# -- -> Boolean
#Return true if any function in this chunk has type MOCK

# --> List of 2
#Return a list of 2 element that show how many lines were added and removed from
#the set of real functions in this chunk.


#If our mock function hasn't actually tracked changes outside of a method
#then we need to replace it with the name of the function stored in header
#Prereq - Have run parse text before this.

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

def replaceKnownAssertHeaders(self, line):
    if("#include" in line):
        line = line.replace("assert.h", "")
        line = line.replace("cassert", "")
        line = line.replace("wtf/Assertions.h", "")
    return line

#Determines if a line of text contains an assertion.
#Precondition - tested line has had all comments and strings removed.
#line is the preprocessed line and fullLine includes the strings and comments
def containsAssert(self, line):
    line = self.replaceKnownAssertHeaders(line)

    if("assert" in line.lower()):
        return True
    else:
        for otherType in self.otherAssertTypes:
            if((otherType + "(") in line): #No lowercase + paren to make mismatch less likely
                if(Util.DEBUG == 1):
                    print("UNUSUAL ASSERT FOUND!")
                    print(line)
                    print(self.otherAssertTypes)
                return True
        return False



#String -> String
#Given a full function String: "<0-n other modifiers> <return_type> <name>(arg0, ..., argN) {"
#Return <name> or "" if the string is not a function header
def parseFunctionName(fullName):
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

    #print("BIGGEST: " + biggest)

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

def isExternBlock(line):
    return(re.search(externPattern, line.strip().lower().replace("\n", "")))

#Determine if the line is a namespace
def isNamespace(line):
    return re.search(namespacePattern, line.strip().lower().replace("\n", ""))

#String --> String
#Given a line, return a pattern for a class declaration if the line ends
#in a class declaration.  Otherwise, return ""
def getClassPattern(line):
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
def extractClassName(line):
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
def isConstructorOrDestructorWithList(line, classContextList):
    result = False
    for nextClass in classContextList:
        result = result or isConstructorOrDestructor(line, nextClass)
        if(result):
            return result

    return result


#Given a string of text and a name of a surrounding class, decide if this is a constructor
#or destructor for the class.
def isConstructorOrDestructor(line, classContext):
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
        print("Checking if a constructor/destructor: " + line)

    return re.search(classContext + paramPattern, temp)









def getExceptionPattern(line):
    result = re.search("\\btry\\b|\\bcatch\\b|\\bthrows\\b", line)
    if(result != None):
        return result.group(0)







#There are many structures that can be mistaken for a function.  We'll try to
#ignore as many of them as possible.
#To start, lets use a regex expression with "<return type> <name> (<0+ parameters>) {"
#Also, we should handle template methods like: "template <class type> <return type> <name<type>>(<0+ parameters>) {""
#Returns a string matching the function pattern or "" if no pattern match found.





def getFunctionPattern(line):
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
    temp = temp.replace("else", "")
    temp = temp.replace("if", "")


    if(Util.DEBUG):
        print("Checking if function: " + line)
    #print "!!!!!! %s" % line

    #Check for regular and template functions
    if("template" in temp):
        temp = temp.replace("static", "") #Quick fix.

        result = re.search(templatePattern1, temp)
        if(result != None):
            return result.group(0)
        result = re.search(templatePattern2, temp)
        if(result != None):
            return result.group(0)
        result = re.search(templatePattern3, temp)
        if(result != None):
            return result.group(0)
        result = re.search(templatePattern4, temp)
        if(result != None):
            return result.group(0)
        result = re.search(templatePattern5, temp)
        if(result != None):
            return result.group(0)
        result = re.search(templatePattern6, temp)
        if(result != None):
            return result.group(0)

        return ""

    else:
        result = re.search(functionPattern1, temp)
        if(result != None):
            return result.group(0)
        result = re.search(functionPattern2, temp)
        if(result != None):
            return result.group(0)
        result = re.search(functionPattern3, temp)
        if(result != None):
            return result.group(0)
        result = re.search(functionPattern4, temp)
        if(result != None):
            return result.group(0)
        result = re.search(functionPattern5, temp)
        if(result != None):
            return result.group(0)
        result = re.search(functionPattern6, temp)
        if(result != None):
            return result.group(0)
        result = re.search(functionPattern7, temp)
        if(result != None):
            phase2=LOOKFOREXCPEND
            return result.group(0)
        result = re.search(functionPattern8, temp)
        if(result != None):
            phase2=LOOKFOREXCPEND
            return result.group(0)


        return ""

def isFunction(self, line):
    return (self.getFunctionPattern(line) != "")

#Determine if the given line is an assignment block using the {
def isAssignment(self, line):
    return re.search(assignPattern, line)

    #Precondition: all the text for this chunk has been read in
    #Postcondition: the self.functions have been parsed out
    #Parameter: fullLog means we are looking at the extended log with
    #everything in the file.  That means we need to remove all functions
    #with 0 additions and deletions.


def parseText(filename):
    ctotal_add=0
    ctotal_del=0
    etotal_add=0
    etotal_del=0
    exceptionBracketDepth=0

    functions = []

    inf = codecs.open(filename, "r", "iso-8859-1")

    initialized = True
    lineNum = 0 # which line we are on, relative to the start of the chunk
    bracketDepth = 0
    lineType = OTHER
    phase = LOOKFORNAME
    phase2= LOOKFOREXCP
    commentFlag = False #Are we inside a comment?
    functionName = ""
    shortFunctionName = ""
    funcStart = 0
    funcEnd = 0
    nestingDepth = 0 # How many brackets should be open to say this function is closed?
    total_add = 0 # How many lines added in this function
    total_del = 0 # How many lines deleted in this function
    classContext = [] #If we are parsing inside a class, what is the closest class name?
    excepDictonary={}


    #Asserts outside of function (1 per chunk)
    assertNoFunc = []
    #Asserts inside the current function
    assertCurFunc = []

    for line in inf:
        lineNum += 1
        if not line.strip():
            continue
        #Remove whitespace on ends.
        fullLine = line.strip()
        line = fullLine


        if(Util.DEBUG==1):
            print("The real line: " + line)

        #Determine if addition, removal, or other
        #if there is a + or -, remove them.
        #Counting the total added and deleted
        #Let's just do it for the contents of the function - i.e.
        #Between { } brackets
        if(line.startswith("+")):
            lineType = ADD
            line = line[1:]
            ctotal_add += 1 #This tracks + for whole chunks.
            #It is necessary for all the normal cases we had before
            #where the function context was correct.
            if(phase == LOOKFOREND):
                total_add += 1
                if(phase2==LOOKFOREXCPEND):
                    etotal_add+=1
                    if str(presentExcep)+" Adds"  in excepDictonary.keys():
                        excepDictonary[str(presentExcep)+" Adds"]+=1
                    else:
                        excepDictonary[str(presentExcep)+" Adds"]=1

        elif(line.startswith("-")):
            lineType = REMOVE
            line = line[1:]
            ctotal_del += 1
            if(phase == LOOKFOREND):
                total_del += 1
                if(phase2==LOOKFOREXCPEND):
                    etotal_del+=1
                    if str(presentExcep)+ " Dels"  in excepDictonary.keys():
                        excepDictonary[str(presentExcep)+" Dels"]+=1
                    else:
                        excepDictonary[str(presentExcep)+" Dels"]=1

        else:
            lineType=OTHER



        #Remove all strings from the line. (Get rid of wierd cases of brackets
        #or comment values being excluded from the line.
        line = re.sub(stringPattern, "", line)

        #If there is a comment of the form /* .... */ (single line only) remove it.
        line = re.sub(commentPattern, "", line)

        #Remove // comments from the string
        line = re.sub(commentPattern2, "", line)

        #print("Next Line: " + line)

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
            if(len(line) > index + 2): #Case where there is code after code end.
                line = line[index + 2:]
            else:
                continue
        elif(commentFlag):
            continue

        #print(str(bracketDepth) + ":" + str(nestingDepth))

        #Extract the name of the function
        if(phase == LOOKFORNAME):
            bracketDepth += line.count("{")


            if(Util.DEBUG == 1):
                print("Current Name Search: " + functionName)

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

                shortFunctionName = getFunctionPattern(functionName)
                if(shortFunctionName != ""):
                    isFunction = True
                    if "throws" in shortFunctionName:
                        phase2=LOOKFOREXCPEND
                        exceptionBlock="throws"
                        presentExcep="throws"
                elif((classContext != [] and isConstructorOrDestructorWithList(functionName, classContext))):
                    isFunction = True
                    shortFunctionName = functionName # don't do the shortening of the pattern for constructor/ destructor
                    #This may be incorrect in general, but I'm just trying to get it to work on the examples I have.
                else:
                    isFunction = False


                #if(not self.isClassDef(functionName) and not self.isAssignment(functionName)): #Skip classes and = {} blocks
                if(isFunction): #Skip things are aren't functions
                    if(Util.DEBUG == 1):
                        print("Function: " + shortFunctionName)
                    funcStart = lineNum
                    phase = LOOKFOREND
                    #Count this line as an addition or deletion
                    #this means either a { will be counted or part
                    #of the function name.  Its close enough to fair
                    #I think
                    if(lineType == REMOVE):
                        total_del = 1
                    elif(lineType == ADD):
                        total_add = 1
                else: #Something that looked like a function at first but wasn't
                    #print("Not function:" + functionName)

                    className = getClassPattern(functionName)
                    if(className != ""):
                        if(Util.DEBUG == 1):
                            print("Class:" + className)
                        classContext.append(extractClassName(className)) #Push onto the class stack
                        nestingDepth += 1 #Functions are inside something now
                    elif(isNamespace(functionName)):
                        if(Util.DEBUG == 1):
                            print("Namespace:" + functionName)
                        nestingDepth += 1 #Functions are inside something now
                    elif(isExternBlock(functionName)):
                        if(Util.DEBUG == 1):
                            print("Extern:" + functionName)
                        nestingDepth +=1

                    else:
                        if(Util.DEBUG == 1):
                            print("Other type of bracket: " + functionName)
                        nestingDepth +=1




                    functionName = "" #Reset name and find next
            else: #No brackets to cut off, so add the whole line instead
                functionName += line.replace("\n", "") + " " #add the line with no new lines


            #print("Current Name: " + functionName)


            #Check for asserts after comments + strings removed
            #This needs to appear here and in the other if statement because we need to
            #handle the case where an assert appears between {} of a one line function

            #Handle case where we have body {} on same line.
            bracketDepth -= line.count("}")
            if(bracketDepth == nestingDepth and phase == LOOKFOREND):
                funcEnd = lineNum

                #Add this function to our list and reset the trackers.
                #We use shortFunctionName, which is the string that matched our expected
                #function pattern regex
                funcToAdd = functionObj(parseFunctionName(shortFunctionName), funcStart, funcEnd, total_add, total_del,etotal_add,etotal_del,excepDictonary)

                #Add assertions from current function
#                funcToAdd.assertionList += assertCurFunc
                functions.append(funcToAdd)

                #Reset asserts to current function
                assertCurFunc = []
                functionName = ""
                shortFunctionName = ""
                funcStart = 0
                funcEnd = 0
                total_add = 0
                total_del = 0
                phase = LOOKFORNAME
                lineType=OTHER

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
                #I know this tracking isn't perfect, so I'm going to relax the
                #context restraints a bit.
                #if(classContext != []):
                #    classContext.pop() #Remove the innermost class from our tracking
                #    if(Util.DEBUG == 1 and classContext != []):
                #        print("New Context is: " + classContext[len(classContext) - 1])


        elif(phase == LOOKFOREND): #determine the end of the function
            #print("Originally: " + str(bracketDepth))
            #print("Line to process: " + line)
           # if "}" in line and "{" not in line:
            #    exceptionBracketDepth=sys.maxint

            bracketDepth -= line.count("}")
            bracketDepth += line.count("{")
            if(exceptionBracketDepth>bracketDepth and phase2==LOOKFOREXCPEND):
                phase2=LOOKFOREXCP
                exceptionBracketDepth=0


            exceptionBlock=getExceptionPattern(line)
            if(exceptionBlock!=None and phase2==LOOKFOREXCP):
                phase2=LOOKFOREXCPEND
                exceptionBracketDepth=bracketDepth
            if exceptionBlock !=None:
                presentExcep=exceptionBlock












            if(Util.DEBUG == 1):
                print("End Check: " + str(bracketDepth))

            #Check for assers after comments + strings removed
            #This needs to appear here and in the other if statement because we need to
            #handle the case where an assert appears between {} of a one line function


            if(bracketDepth == nestingDepth):
                funcEnd = lineNum
                #Add this function to our list and reset the trackers.
                if(Util.DEBUG == 1):
                  print(str(funcStart) + " : " + str(funcEnd))
                funcToAdd = functionObj(parseFunctionName(shortFunctionName), funcStart, funcEnd, total_add, total_del,etotal_add,etotal_del,excepDictonary)

                #Add assertions from current function
                funcToAdd.assertionList += assertCurFunc
                functions.append(funcToAdd)

                #Reset asserts to current function
                assertCurFunc = []
                functionName = ""
                shortFunctionName = ""
                funcStart = 0
                funcEnd = 0
                total_add = 0
                total_del = 0
                etotal_add = 0
                etotal_del = 0
                phase = LOOKFORNAME
                phase2 = LOOKFOREXCP
                exceptionBracketDepth=0
                excepDictonary={}



    #Suppose we have a function where only the top is modified,
    # e.g.
    # int renamedFunction(int arg1) {
    #   int x = 0;
    #Then we want to add this into the count.

    if(shortFunctionName != ""):
        #The end of the function will be said to be the cutoff of the change.
        funcEnd = lineNum
        funcToAdd = functionObj(parseFunctionName(shortFunctionName), funcStart, funcEnd, total_add, total_del,etotal_add,etotal_del,excepDictonary)
        #Add assertions from current function
        #funcToAdd.assertionList += assertCurFunc
        functions.append(funcToAdd)


    #Create a mock function for any asserts that do not fall into another function's list
    # if assertNoFunc:
    #     mockFunction = functionObj(MOCK, 0, 0, 0, 0)
    #     mockFunction.assertionList += assertNoFunc
    #     self.functions.append(mockFunction)

    #Remove unmodified functions if necessary.
    functions = filter(lambda(x) : x.total_add != 0 or x.total_del != 0 or x.name == "Mock_Function_For_Asserts", functions)



    for x in functions:
        print "Function: ",x.name
        print "Total Adds: ",x.total_add
        print "Totals Dels: ",x.total_del
        print "Total Exception adds: ",x.total_excep_add
        print "Total Exception dels: ",x.total_excep_del
        for key,val in x.excepDict.items():
            print key,val
        print "========================================="





if __name__ == '__main__':
    parseText("all_log.txt")