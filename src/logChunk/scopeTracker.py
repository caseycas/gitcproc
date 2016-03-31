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


#Redo with a polymorphic solution for the languages
class scopeTracker:
    #string --> -- 
    #The language tells how the scope changes so we can tell when a block or function ends.
    #For example in C/C++ and Java, a { signifies a increase in code block depth.
    #In python however, indentation is used.
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
    def scopeOrder(self, line, lineType): #Seems to only matter in Bracket Languages
        raise NotImplementedError("Base ScopeTracker is Abstract.")
        
    def scopeIncreaseCount(self, line, lineType): #Seems to only matter in Bracket Languages
        raise NotImplementedError("Base ScopeTracker is Abstract.")

    def scopeDecreaseCount(self, line, lineType): #Seems to only matter in Bracket Languages
        raise NotImplementedError("Base ScopeTracker is Abstract.")

    #Returns true if this line contains an increased level of scope.
    def isScopeIncrease(self, line, lineType):
        raise NotImplementedError("Base ScopeTracker is Abstract.")

    #Returns true if this line contains an decreased level of scope.
    def isScopeDecrease(self, line, lineType):
        raise NotImplementedError("Base ScopeTracker is Abstract.")

    def appendFunctionEnding(self, line, functionName):
        raise NotImplementedError("Base ScopeTracker is Abstract.")

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

    #string, [ADD|REMOVE|OTHER], [GENERIC|FUNC|BLOCK] -> --
    #Increase the depth of our tracker and add in function or block contexts if they have been discovered.
    def increaseScope(self, line, lineType, changeType):
        raise NotImplementedError("Base ScopeTracker is Abstract.")

    #string, [ADD|REMOVE|OTHER] -> --
    #Decrease our current scope and close out any function or block contexts if necessary.
    def decreaseScope(self, line, lineType):
        raise NotImplementedError("Base ScopeTracker is Abstract.")

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
