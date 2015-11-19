import sys
import re
from PatchMethod import PatchMethod

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

#LineTypes
ADD = 1
REMOVE = 2
OTHER = 3

stringPattern = "\".*\""
commentPattern = "/\*.*\*/"
commentPattern2 = "//.*"
parenPattern = "\(.*\)"
assignPattern = "= *{"
paramPattern = " *\([\w\d_,\[\]\*\(\)&: ]*\)[^;]*{" #What parameters to a call look like.
functionPattern1 = "[\w\d_]+ *\** +[\w\d_:]+&* *\([\w\d_,\[\]\*\(\)&: ]*\) *{$"
functionPattern2 = "[\w\d_]+ +\** *[\w\d_:]+&* *\([\w\d_,\[\]\*\(\)&: ]*\) *{$"
#functionPattern3 = "[\w\d_]+ *\** *[\w\d_:]+&* *\([\w\d_,\[\]\*\(\)&: ]*\) const *{$"
functionPattern3 = functionPattern2

templatePattern1 = "template +< *class +.*> +[\w\d_]+ *\** +[\w\d_<>:]+ *\([\w\d_,\[\]\*\(\)&: ]*\) *{$"
templatePattern2 = "template +< *class +.*> +[\w\d_]+ +\** *[\w\d_<>:]+ *\([\w\d_,\[\]\*\(\)&: ]*\) *{$"
MOCK = "Mock_Function_For_Asserts"

#A text file for function that we know are asserts, but don't use
#the word assert in their names
otherAssertFile = "assertFunctions.txt" 

class functionObj:

    def __init__(self, name, start=0, end=0, added=0, deleted=0):
        self.name = name
        self.start = start
        self.end = end
        self.assertionList = [] #List of triples - line #, line type, actual assert
        self.total_add = added
        self.total_del = deleted

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
class logChunk:
    def __init__(self, text = ""):
        self.text = text
        self.functions = []
        self.initialized = False
        self.total_add = 0
        self.total_del = 0
        self.otherAssertTypes = self.readKnownTypes()
        self.header = "" #What is the name given after '@@' in log

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
    def hasMockFunction(self):
        for func in self.functions:
            if(func.name == MOCK):
                #func.printFunc()
                return True

        return False

    #If our mock function hasn't actually tracked changes outside of a method
    #then we need to replace it with the name of the function stored in header
    #Prereq - Have run parse text before this.
    def convertMockToReal(self):
        assert(self.header != "" and self.hasMockFunction()) #This function requires header to be set to something
        if(self.header != "NA" and len(self.functions) == 1): #If NA, then this really needs a mock function
            self.functions[0].name = self.header
            self.functions[0].total_add = self.total_add
            self.functions[0].total_del = self.total_del

    #Check if what we've seen in the header mismatches what is in the chunk
    #Prereq - Have run parse text before this.
    def isHeaderMismatch(self):
        if(self.header == ""):
            print(self.text)
        assert(self.header != "")
        if(len(self.functions) > 1):
            return True
        elif(len(self.functions) == 1):
            if(self.functions[0].name == MOCK):
                return False
            elif(self.functions[0].name != self.header):
                return True
            else:
                return False
        elif(len(self.functions) == 0):
            return False
        else:
            assert(0)

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

    #Determines if a line of text contains an assertion.
    #Precondition - tested line has had all comments and strings removed.
    #line is the preprocessed line and fullLine includes the strings and comments
    def containsAssert(self, line):
        if("#include" in line):
            line = line.replace("assert.h", "")
            line = line.replace("cassert", "")

        if("assert" in line.lower()):
            return True
        else:
            for otherType in self.otherAssertTypes:
                if((otherType + "(") in line): #No lowercase + paren to make mismatch less likely
                    print("UNUSUAL ASSERT FOUND!")
                    print(line)
                    print(self.otherAssertTypes)
                    return True
            return False

        

    #String -> String
    #Given a full function String: "<0-n other modifiers> <return_type> <name>(arg0, ..., argN) {"
    #Return <name> or "" if the string is not a function header
    def parseFunctionName(self, fullName):
        if(fullName.find("\n") != -1):
            fullName = fullName.replace("\n", "")

        #print("Name: " + fullName)
        results = re.findall(parenPattern, fullName)
        #Since types can be of (), we want to find the index of the last and largest match to (.*)
        #Prefer largest, but if multiple equal size (i.e. returns a type with () and has no arguments)
        #get the later one.
        max = -1
        biggest = ""
        for r in results:
            if(max <= len(r)):
                max = len(r)
                biggest = r
        
        if(biggest == ""):
            #raise ValueError("This line doesn't seem to be a function header", fullName)
            return "" #If not a function name - return nothing.

        #Get start index of last copy of biggest
        argStart = fullName.rfind(biggest)
        if(argStart == -1):
            raise ValueError("Regex said we found argument section, but now we can't find it.", fullName)

        #Break up the string prior to the () section
        pieces = fullName[0:argStart].split(" ")
        for next in reversed(pieces):
            if(next != ""):
                #print("Return: " + next.strip())
                return next.strip()

        raise ValueError("Couldn't find method name", fullName)


    #Determine whether the given line is the begining of a class,
    #which can be confused with a function definition.
    def isClassDef(self, line):
        components = line.lower().split()
        if(len(components) < 2): # A class needs class + name at the minimum
            return False
        elif (components[0] == "class"):
            return True
        elif (components[0] == "template"): #Identify template classes
            if("<class" in components and "class" in components):
                return True
            elif(components.count("class") == 2): #They put a space in: e.g. template < class T > class example {
                return True
            else: #This is a template method rather than a class.
                return False
        else:
            return False

    #Given a string of text that is a class name, extract the name of the class
    def extractClassName(self, line):
        components = line.split()
        return components[1];

    #Given a string of text and a name of a surrounding class, decide if this is a constructor
    #for the class.
    def isConstructor(self, line, classContext):
        return re.search(classContext + paramPattern, line.strip().replace("\n", ""))

    #There are many structures that can be mistaken for a function.  We'll try to
    #ignore as many of them as possible.
    #To start, lets use a regex expression with "<return type> <name> (<0+ parameters>) {"
    #Also, we should handle template methods like: "template <class type> <return type> <name<type>>(<0+ parameters>) {""
    def isFunction(self, line):
        temp = line.strip().replace("\n", "")
        if(line.startswith("else if")):
            return False

	    #print "!!!!!! %s" % line
        
        #Check for regular and template functions
        if("template" in temp):
            return re.search(templatePattern1, temp) or re.search(templatePattern2, temp)
        else:
            return re.search(functionPattern1, temp) or re.search(functionPattern2, temp) \
                or re.search(functionPattern3, temp) #or re.search(functionPattern4, temp)

    #Determine if the given line is an assignment block using the {
    def isAssignment(self, line):
        return re.search(assignPattern, line)        

    #Precondition: all the text for this chunk has been read in
    #Postcondition: the self.functions have been parsed out
    def parseText(self):

        self.initialized = True
        lineNum = 0 # which line we are on, relative to the start of the chunk
        bracketDepth = 0
        funcBracketDepth = 0 #bray: some times bracketDepth is taken by namescope etc.
        lineType = OTHER
        phase = LOOKFORNAME
        commentFlag = False #Are we inside a comment?
        functionName = ""
        funcStart = 0
        funcEnd = 0
        nestingDepth = 0 # How many brackets should be open to say this function is closed?
        funcNestingDepth = 0
        total_add = 0 # How many lines added in this function
        total_del = 0 # How many lines deleted in this function
        classContext = [] #If we are parsing inside a class, what is the closest class name?


        #Asserts outside of function (1 per chunk)
        assertNoFunc = []
        #Asserts inside the current function
        assertCurFunc = []

        for line in self.text.split("\n"):
            lineNum += 1
            #Remove whitespace on ends.
            fullLine = line.strip()
            line = fullLine
            
            #Determine if addition, removal, or other
            #if there is a + or -, remove them.
            #Counting the total added and deleted
            #Let's just do it for the contents of the function - i.e.
            #Between { } brackets
            if(line.startswith("+")):
                lineType = ADD
                line = line[1:]
                self.total_add += 1 #This tracks + for whole chunks.
                #It is necessary for all the normal cases we had before
                #where the function context was correct.
                if(phase == LOOKFOREND):
                    total_add += 1
            elif(line.startswith("-")):
                lineType = REMOVE
                line = line[1:]
                self.total_del += 1
                if(phase == LOOKFOREND):    
                    total_del += 1
            else:
                continue #Skip lines that aren't added or removed
                #lineType = OTHER

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
                continue
            elif(line.find("*/") != -1): #TODO: Case where there is stuff past the end?
                commentFlag = False
                continue
            elif(commentFlag):
                continue

            if Util.DEBUG == 1:
                print("========\n +++ line : " + line) 
                print("funcBracketDepth  : funcNestingDepth = %d : %d" % (funcBracketDepth, funcNestingDepth))
                print("bracketDepth  : nestingDepth = %d : %d" % (bracketDepth, nestingDepth))
              

              

            #Extract the name of the function
            if(phase == LOOKFORNAME):
                #Check if this is the start of a function name.
                
                functionName += line.replace("\n", "") + " " #add the line with no new lines
                
                bracketDepth += line.count("{")
                funcBracketDepth += line.count("{")
                
                if Util.DEBUG == 1:
                    print("Current Function Name: " + functionName)

                #What if we've hit a function defintion?
                if(line.strip().endswith(";")):
                    functionName = "" #Clear the name

                if(funcBracketDepth > funcNestingDepth):
                    #Add last line of name (everything before first "{")
                    
                    functionName += line.split("{")[0]
                    if Util.DEBUG == 1:
                        print "==== functionName : %s" % functionName
                    
                    #if(not self.isClassDef(functionName) and not self.isAssignment(functionName)): #Skip classes and = {} blocks
                    if(self.isFunction(functionName) or \
                        (classContext != [] and self.isConstructor(functionName, classContext[len(classContext) - 1]))): #Skip things are aren't functions
                        if Util.DEBUG == 1:
                            print("!!! Found Function: " + functionName)
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
                    else:
                        #print("Not function:" + functionName)
                        if(self.isClassDef(functionName)):
                            if Util.DEBUG == 1:
                                print("Class:" + functionName)
                            classContext.append(self.extractClassName(functionName)) #Push onto the class stack
                            nestingDepth += 1 #Functions are inside something now
                            
                        functionName = "" #Reset name and find next
                        funcBracketDepth = 0
                
                        
                if Util.DEBUG == 1:
                    print("==== Current Function Name : " + functionName)


                #Check for assers after comments + strings removed
                #This needs to appear here and in the other if statement because we need to
                #handle the case where an assert appears between {} of a one line function
                if(self.containsAssert(line)):
                    if(phase == LOOKFOREND): #Assert is inside a function
                        assertCurFunc.append((lineNum, lineType, fullLine))
                    elif(phase == LOOKFORNAME): #Assert is not inside a function
                        assertNoFunc.append((lineNum, lineType, fullLine))
                    else:
                        assert(0); # not a valid phase   

                #Handle case where we have body {} on same line.   
                bracketDepth -= line.count("}")
                if funcBracketDepth > 0:
                    funcBracketDepth -= line.count("}")
                #print "funcBracketDepth = %s" % funcBracketDepth
                if((funcBracketDepth == funcNestingDepth or bracketDepth == nestingDepth) and phase == LOOKFOREND):
                    funcEnd = lineNum

                    #Add this function to our list and reset the trackers.
                    funcToAdd = functionObj(self.parseFunctionName(functionName), \
                        funcStart, funcEnd, total_add, total_del)
                    
                    #Add assertions from current function
                    funcToAdd.assertionList += assertCurFunc
                    self.functions.append(funcToAdd)
              
                    #Reset asserts to current function
                    assertCurFunc = []
                    functionName = ""
                    funcStart = 0
                    funcEnd = 0
                    total_add = 0
                    total_del = 0
                    phase = LOOKFORNAME

                #Set back the expected level for seeing the start of functions
                if(bracketDepth < nestingDepth):
                    nestingDepth = bracketDepth
                    if(classContext != []):
                        classContext.pop() #Remove the innermost class from our tracking

                if(funcBracketDepth < funcNestingDepth):
                    funcNestingDepth = funcBracketDepth

            elif(phase == LOOKFOREND): #determine the end of the function
                bracketDepth += line.count("{")
                bracketDepth -= line.count("}")

                funcBracketDepth += line.count("{")
                if funcBracketDepth > 0:
                    funcBracketDepth -= line.count("}")
                


                #Check for assers after comments + strings removed
                #This needs to appear here and in the other if statement because we need to
                #handle the case where an assert appears between {} of a one line function
                if(self.containsAssert(line)):
                    if(phase == LOOKFOREND): #Assert is inside a function
                        assertCurFunc.append((lineNum, lineType, fullLine))
                    else:
                        assert(0); # not a valid phase  

                if(funcBracketDepth == funcNestingDepth or bracketDepth == nestingDepth):
                    funcEnd = lineNum
                    #Add this function to our list and reset the trackers.
                    #print(str(funcStart) + " : " + str(funcEnd))
                    funcToAdd = functionObj(self.parseFunctionName(functionName), funcStart, funcEnd, total_add, total_del)
                    
                    #Add assertions from current function
                    funcToAdd.assertionList += assertCurFunc
                    self.functions.append(funcToAdd)
              
                    #Reset asserts to current function
                    assertCurFunc = []
                    functionName = ""
                    funcStart = 0
                    funcEnd = 0
                    total_add = 0
                    total_del = 0
                    phase = LOOKFORNAME

        #Create a mock function for any asserts that do not fall into another function's list
        if assertNoFunc:
            mockFunction = functionObj(MOCK, 0, 0, 0, 0)
            mockFunction.assertionList += assertNoFunc
            self.functions.append(mockFunction)

            
