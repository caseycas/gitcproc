import sys
import re

sys.path.append("../util")

import Util
import UnsupportedLanguageException
from chunkingConstants import *
from scopeTracker import *

#Scope Tracking in Python
#Can not mix Tabs and WhiteSpaces
#Indent level not specific


#Redo with a polymorphic solution for the languages
class IndentScopeTracker:
    def __init__(self, language):
        #These are pseudo stacks implemented as lists that track the current 
        #number of open scopes (brackets, tabs, etc), each change gets its own
        #entry, which is then deleted when we see a matching closing entry
        #Functions and blocks are included in full so they can be matched later
        self.oldVerStack = []
        self.newVerStack = []
        self.indentToken = "" #This tells us what the indent token for the file is.  Can be a number of spaces or tab
        self.lastOldFuncContext = ""
        self.lastOldBlockContext = []
        self.lastNewFuncContext = ""
        self.lastNewBlockContext = []
        self.language = language

    #String -> list
    #Returns a list giving the sequence of scope changes in this line.
    def scopeOrder(self, line, lineType):
        if(isScopeIncrease(line,lineType)):
            return [INCREASE]
        elif(isScopeDecrease(line,lineType)):
            return [DECREASE]
        else:
            return []
        
    def scopeIncreaseCount(self, line, lineType):
        if(self.isScopeIncrease(line,lineType)):
            return 1
        else:
            return 0

    def scopeDecreaseCount(self, line, lineType):
        if(self.isScopeDecrease(line, lineType)):
            return 1
        else:
            return 0

    def indentDepth(self, whiteSpace):
        #Make sure there is no mixing of tabs and spaces
        assert(self.indentToken != "")
        if(self.indentToken == "\t"):
            assert(" " not in whiteSpace)
        else:
            assert("\t" not in whiteSpace)

        return len(re.findAll(self.indentToken, whiteSpace))

    #Returns true if this line contains an increased level of scope.
    #One possible concern here is a single statement spread over multiple lines.  I don't think that would cause
    #issues if we treat them like any other indent, but it could be a problem.
    def isScopeIncrease(self, line, lineType):
        #Match beginning whitespace.  Credit to kennytm here: 
        #http://stackoverflow.com/questions/2268532/grab-a-lines-whitespace-indention-with-python
        indent = re.match(r"\s*", line).group() 
        if(indent != ""):
            if(self.indentToken == ""): #Is this the first indent in the file?  Use this to determine future indentation
                self.indentToken = indent
                return True
            else:
                #How deep is the indent?
                depth = self.indentDepth(indent)
                if(lineType == ADD):
                    return len(newVerStack) < depth
                elif(lineType == REMOVE):
                    return len(oldVerStack) < depth
                elif(lineTYPE == OTHER): #Can these be different?
                    return len(oldVerStack) < depth or len(newVerStack) < depth #If these are different, just adjust the stack accordingly
                else:
                    assert("Not a valid line type")
        else:
            return False


    #Returns true if this line contains an decreased level of scope.
    def isScopeDecrease(self, line):
        assert(self.indentToken != "") #If Scope is decreasing, if must have increased at some point
        depth = indentDepth(indent)
        if(lineType == ADD):
            return len(newVerStack) > depth
        elif(lineType == REMOVE):
            return len(oldVerStack) > depth
        elif(lineTYPE == OTHER): #Can these be different?
            return len(oldVerStack) > depth or len(newVerStack) > depth #If these are different, just adjust the stack accordingly
        else:
            assert("Not a valid line type")

    def appendFunctionEnding(self, line, functionName):
        return functionName #Nothing to do here

    def increaseNewIndent(self, line, changeType):
        if(changeType == GENERIC):
            self.newVerStack.append((indent, GENERIC)) #Should be able to increase only 1 level at a time?
        elif(changeType == FUNC):
            self.newVerStack.append((line, FUNC))
            self.lastNewFuncContext = line
        elif(changeType == SBLOCK):
            self.newVerStack.append((line, SBLOCK))
            self.lastNewBlockContext.append(line)
        else:
            assert("Not a valid change type.")

    def increaseOldIndent(self, line, changeType):
        if(changeType == GENERIC):
            self.oldVerStack.append((indent, GENERIC)) #Should be able to increase only 1 level at a time?
        elif(changeType == FUNC):
            self.oldVerStack.append((line, FUNC))
            self.lastOldFuncContext = line
        elif(changeType == SBLOCK):
            self.oldVerStack.append((line, SBLOCK))
            self.lastOldBlockContext.append(line)
        else:
            assert("Not a valid change type.")

    #string, [ADD|REMOVE|OTHER], [GENERIC|FUNC|BLOCK] -> --
    #Increase the depth of our tracker and add in function or block contexts if they have been discovered.
    def increaseScope(self, line, lineType, changeType):
        if(lineType == ADD):
            self.increaseNewIndent(line, changeType)
        elif(lineType == REMOVE):
            self.increaseOldIndent(line, changeType)
        elif(lineType == OTHER): 
            #TODO: How do I handle this now.
            #If increase relative to old th
            depth = self.indentDepth(line)
            isOldIncrease = len(oldVerStack) < depth
            isNewIncrease = len(newVerStack) < depth
            assert(isOldIncrease or isNewIncrease)
            if(isOldIncrease):
                self.increaseOldIndent(line, changeType)
            if(isNewIncrease):
                self.increaseNewIndent(line, changeType)
        else:
            assert("Not a valid line type")


    #Remove indents from the new stack and update the functional and block caches accordingly
    def decreaseNewIndent(self, line):
        if(self.newVerStack != []):
            removed = self.newVerStack.pop()
            if(Util.DEBUG):
                print("Removing: " + str(removed))
                print("Context: " + str(self.lastNewBlockContext))
            if(removed[LABELINDEX] == FUNC):
                self.lastNewFuncContext = self.getTopType(self.newVerStack, FUNC)
            elif(removed[LABELINDEX] == SBLOCK):
                self.lastNewBlockContext.remove(removed[LINEINDEX])
        else:#Bracket overclosing -> estimating...
            if(Util.DEBUG):
                print("Popped from empty new Stack.")

    #Remove indents from the old stack and update the functional and block caches accordingly
    def decreaseOldIndent(self, line):
        if(self.oldVerStack != []):
            removed = self.oldVerStack.pop()
            if(Util.DEBUG):
                print("Removing: " + str(removed))
                print("Context: " + str(self.lastOldBlockContext))
            if(removed[LABELINDEX] == FUNC):
                self.lastOldFuncContext = self.getTopType(self.oldVerStack, FUNC)
            elif(removed[LABELINDEX] == SBLOCK):
                self.lastOldBlockContext.remove(removed[LINEINDEX])
        else:#Bracket overclosing -> estimating...
            if(Util.DEBUG):
                print("Popped from empty old Stack.")

    #string, [ADD|REMOVE|OTHER] -> --
    #Decrease our current scope and close out any function or block contexts if necessary.
    def decreaseScope(self, line, lineType):
        if(lineType == ADD):
            self.decreaseNewIndent(line, changeType)
        elif(lineType == REMOVE):
            self.decreaseOldIndent(line, changeType)
        elif(lineType == OTHER): 
            #TODO: How do I handle this now.
            #If increase relative to old th
            depth = self.indentDepth(line)
            isOldDecrease = len(oldVerStack) > depth
            isNewDecrease = len(newVerStack) > depth
            assert(isOldDecrease or isNewDecrease)
            if(isOldDecrease):
                self.decreaseOldIndent(line, changeType)
            if(isNewDecrease):
                self.decreaseNewIndent(line, changeType)
        else:
            assert("Not a valid line type")