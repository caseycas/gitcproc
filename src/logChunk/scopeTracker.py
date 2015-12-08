import sys
import re

sys.path.append("../util")

import Util
import UnsupportedLanguageException
from chunkingConstants import *

# Types of elements on our version stacks
FUNC = "Function"
SBLOCK = "Block"
GENERIC = "Generic"
LINEINDEX = 0
LABELINDEX = 1

BracketLanguages = ["C", "C++", "Java"]


class scopeTracker:
    #string --> -- 
    #The language tells how the scope changes so we can tell when a block or function ends.
    #For example in C/C++ and Java, a { signifies a increase in code block depth.
    #In python however, 4 spaces are used.
    def __init__(self, language):
        #These are pseudo stacks implemented as lists that track the current 
        #number of open scopes (brackets, tabs, etc), each change gets its own
        #entry, which is then deleted when we see a matching closing entry
        #Functions and blocks are included in full so they can be matched later
        self.oldVerStack = []
        self.newVerStack = []
        self.lastOldFuncContext = ""
        self.lastOldBlockContext = []
        self.lastNewFuncContext = ""
        self.lastNewBlockContext = []
        if(language in Util.supportedLanguages):
            self.language = language
        else:
            raise UnsupportedLanguageException(language + "is not yet supported.")

    def clearScope(self):
        self.oldVerStack = []
        self.newVerStack = []
        self.lastOldFuncContext = ""
        self.lastOldBlockContext = []
        self.lastNewFuncContext = ""
        self.lastNewBlockContext = []

    #String -> list
    #Returns a list giving the sequence of scope changes in this line.
    def scopeOrder(self, line):
        scopeOrderChanges = []
        #Thanks to http://stackoverflow.com/questions/4664850/find-all-occurrences-of-a-substring-in-python
        if(self.language in BracketLanguages):
            increaseIndicies = [next.start() for next in re.finditer('{', line)] 
            decreaseIndicies = [next.start() for next in re.finditer('}', line)]
            j = 0
            k = 0
            iLen = len(increaseIndicies)
            dLen = len(decreaseIndicies)
            for i in range(0, iLen + dLen):
                #assert(j < iLen and k < dLen)
                if(j == iLen and k < dLen):
                    scopeOrderChanges.append(DECREASE)
                    k += 1
                elif(k == dLen and j < iLen):
                    scopeOrderChanges.append(INCREASE)
                    j += 1
                elif(increaseIndicies[j] < decreaseIndicies[k]):
                    scopeOrderChanges.append(INCREASE)
                    j += 1
                else:
                    scopeOrderChanges.append(DECREASE)
                    k += 1

            return scopeOrderChanges
        else:
            raise UnsupportedLanguageException(language + "is not yet supported.")
        
    def scopeIncreaseCount(self, line):
        if(self.language in BracketLanguages):
            return line.count("{")
        else:
            raise UnsupportedLanguageException(language + "is not yet supported.")

    def scopeDecreaseCount(self, line):
        if(self.language in BracketLanguages):
            return line.count("}")
        else:
            raise UnsupportedLanguageException(language + "is not yet supported.")

    #Returns true if this line contains an increased level of scope.
    def isScopeIncrease(self, line):
        if(self.language in BracketLanguages):
            return line.count("{") > 0
        else:
            raise UnsupportedLanguageException(language + "is not yet supported.")

    #Returns true if this line contains an decreased level of scope.
    def isScopeDecrease(self, line):
        if(self.language in BracketLanguages):
            return line.count("}") > 0
        else:
            raise UnsupportedLanguageException(language + "is not yet supported.")

    def appendFunctionEnding(self, line, functionName):
        if(self.language in BracketLanguages):
            if("{" in line):
                functionName += line.split("{")[0] + "{"
            else:
                functionName += line.split("{")[0]
            return functionName
        else:
            raise UnsupportedLanguageException(language + "is not yet supported.")

    #Returns true if both oldVerStack and newVerStack are empty.
    def areAllContextsClosed(self):
        return self.oldVerStack == [] and self.newVerStack == []

    #Returns a tuple of lists of open function and block contexts in the old and new versions of the
    #program.  If all contexts are closed (matching brackets in C/C++, no indent in python)
    #returns an empty list
    def listOpenContexts(self):
        return ([o for o in oldVerStack if o[LABELINDEX] == SBLOCK or o[LABELINDEX] == FUNC], 
                [n for n in newVerStack if n[LABELINDEX] == SBLOCK or n[LABELINDEX] == FUNC])

    #list of tuples, label [FUNC|BLOCK|GENERIC] -> string
    #Given a list with tuples of string and a label, and a choosen label, return the string of the last
    #item in the list that matches that label.  If nothing in the stack is found for that label, return
    #"" instead.
    def getTopType(self, stack, stackType):
        for item in reversed(stack):
            if(item[LABELINDEX] == stackType):
                return item[LINEINDEX]

        return "" 

    #Add "{" from the new stack and update the functional and block caches accordingly
    def increaseNewBrackets(self, line, changeType):
        if(changeType == GENERIC):
            for i in range(0, line.count("{")):
                self.newVerStack.append(("{", GENERIC))
        elif(changeType == FUNC):
            self.newVerStack.append((line, FUNC))
            self.lastNewFuncContext = line
        elif(changeType == SBLOCK): #Consider this carefully for when we get the opening {...
            self.newVerStack.append((line, SBLOCK))
            self.lastNewBlockContext.append(line)
        else:
            assert("Not a valid change type.")

    #Add "{" from the old stack and update the functional and block caches accordingly
    def increaseOldBrackets(self, line, changeType):
        if(changeType == GENERIC):
            for i in range(0, line.count("{")):
                self.oldVerStack.append(("{", GENERIC))
        elif(changeType == FUNC):
            self.oldVerStack.append((line, FUNC))
            self.lastOldFuncContext = line
        elif(changeType == SBLOCK): #Consider this carefully for when we get the opening {...
            self.oldVerStack.append((line, SBLOCK))
            self.lastOldBlockContext.append(line)
        else:
            assert("Not a valid change type.")

    #string, [ADD|REMOVE|OTHER], [GENERIC|FUNC|BLOCK] -> --
    #Increase the depth of our tracker and add in function or block contexts if they have been discovered.
    def increaseScope(self, line, lineType, changeType):
        if(lineType == ADD):
            if(self.language in BracketLanguages):
                self.increaseNewBrackets(line, changeType)
            else:
                raise UnsupportedLanguageException(language + "is not yet supported.")
        elif(lineType == REMOVE):
            if(self.language in BracketLanguages):
                self.increaseOldBrackets(line, changeType)
            else:
                raise UnsupportedLanguageException(language + "is not yet supported.")
        elif(lineType == OTHER):
            if(self.language in BracketLanguages):
                self.increaseOldBrackets(line, changeType)
                self.increaseNewBrackets(line, changeType)
            else:
                raise UnsupportedLanguageException(language + "is not yet supported.")
        else:
            assert("Not a valid line type")

    #Remove "}" from the new stack and update the functional and block caches accordingly
    def decreaseNewBrackets(self, line):
        for i in range(0, line.count("}")):
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
                break

    #Remove "}" from the old stack and update the functional and block caches accordingly
    def decreaseOldBrackets(self, line):
        for i in range(0, line.count("}")):
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
                    print("Popped from empty new Stack.")
                break

    #string, [ADD|REMOVE|OTHER] -> --
    #Decrease our current scope and close out any function or block contexts if necessary.
    def decreaseScope(self, line, lineType):
        if(lineType == ADD):
            if(self.language in BracketLanguages):
                self.decreaseNewBrackets(line)
            else:
                raise UnsupportedLanguageException(language + "is not yet supported.")
        elif(lineType == REMOVE):
            if(self.language in BracketLanguages):
                self.decreaseOldBrackets(line)
            else:
                raise UnsupportedLanguageException(language + "is not yet supported.")
        elif(lineType == OTHER):
            if(self.language in BracketLanguages):
                self.decreaseOldBrackets(line)
                self.decreaseNewBrackets(line)
            else:
                raise UnsupportedLanguageException(language + "is not yet supported.")
        else:
            assert("Not a valid line type")

    #Return the surrounding functional context or "" if not on the stack
    def getFuncContext(self, lineType):
        if(lineType == ADD or lineType == OTHER):
            return self.lastNewFuncContext
        elif(lineType == REMOVE):
            return self.lastOldFuncContext
        else:
            assert("Not a valid line type")

    #Return the surrounding block contexts or [] if not on the stack
    def getBlockContext(self, lineType):
        if(lineType == ADD or lineType == OTHER):
            return self.lastNewBlockContext
        elif(lineType == REMOVE):
            return self.lastOldBlockContext
        else:
            assert("Not a valid line type")

    #A debug function for printing the objects variables.
    def printScope(self):
        print("------------------<Scope Obj>------------------")
        print("Language:")
        print(self.language)
        print("Old Stack:")
        print(self.oldVerStack)
        print("Old Func Cache:")
        print(self.lastOldFuncContext)
        print("Old Block Cache:")
        print(self.lastOldBlockContext)
        print("New Stack:")
        print(self.newVerStack)
        print("New Func Cache:")
        print(self.lastNewFuncContext)
        print("New Block Cache:")
        print(self.lastNewBlockContext)
        print("------------------<Scope Obj>------------------")

