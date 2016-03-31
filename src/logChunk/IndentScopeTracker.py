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
class IndentScopeTracker:
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
        self.language = language

    #String -> list
    #Returns a list giving the sequence of scope changes in this line.
    def scopeOrder(self, line):
        raise NotImplementedError("Base ScopeTracker is Abstract.")
        
    def scopeIncreaseCount(self, line):
        raise NotImplementedError("Base ScopeTracker is Abstract.")

    def scopeDecreaseCount(self, line):
        raise NotImplementedError("Base ScopeTracker is Abstract.")

    #Returns true if this line contains an increased level of scope.
    def isScopeIncrease(self, line):
        raise NotImplementedError("Base ScopeTracker is Abstract.")

    #Returns true if this line contains an decreased level of scope.
    def isScopeDecrease(self, line):
        raise NotImplementedError("Base ScopeTracker is Abstract.")

    def appendFunctionEnding(self, line, functionName):
        raise NotImplementedError("Base ScopeTracker is Abstract.")

    #Returns true if both oldVerStack and newVerStack are empty.
    def areAllContextsClosed(self):
        return self.oldVerStack == [] and self.newVerStack == []

    #string, [ADD|REMOVE|OTHER], [GENERIC|FUNC|BLOCK] -> --
    #Increase the depth of our tracker and add in function or block contexts if they have been discovered.
    def increaseScope(self, line, lineType, changeType):
        raise NotImplementedError("Base ScopeTracker is Abstract.")

    #string, [ADD|REMOVE|OTHER] -> --
    #Decrease our current scope and close out any function or block contexts if necessary.
    def decreaseScope(self, line, lineType):
        raise NotImplementedError("Base ScopeTracker is Abstract.")