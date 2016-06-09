import sys
import re
sys.path.append("../util")
import Util
import UnsupportedLanguageException
from chunkingConstants import *
from scopeTracker import *


#Redo with a polymorphic solution for the languages
class BracketScopeTracker(scopeTracker):
    #string --> -- 
    #The language tells how the scope changes so we can tell when a block or function ends.
    #For example in C/C++ and Java, a { signifies a increase in code block depth.
    #In python however, 4 spaces are used.
    def __init__(self, language, c_info):
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
        self.isContinuation = False
        self.config_info = c_info


    def clearScope(self):
        self.oldVerStack = []
        self.newVerStack = []
        self.lastOldFuncContext = ""
        self.lastOldBlockContext = []
        self.lastNewFuncContext = ""
        self.lastNewBlockContext = []

    #String -> list
    #Returns a list giving the sequence of scope changes in this line.
    def scopeOrder(self, line, lineType):
        scopeOrderChanges = []
        #Thanks to http://stackoverflow.com/questions/4664850/find-all-occurrences-of-a-substring-in-python
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
        
    def scopeIncreaseCount(self, line, lineType):
        return line.count("{")

    def scopeDecreaseCount(self, line, lineType):
        return line.count("}")

    #Returns true if this line contains an increased level of scope.
    def isScopeIncrease(self, line, lineType):
        if(line.count("{") > 0):
            return S_YES
        else: 
            return S_NO

    #Returns true if this line contains an decreased level of scope.
    def isScopeDecrease(self, line, lineType):
        if(line.count("}") > 0):
            return S_YES
        else:
            return S_NO

    def isFunctionalScopeChange(self, line, lineType):
        return self.isScopeIncrease(line, lineType)

    def handleFunctionNameEnding(self, line, functionName, lineType, funcIdentFunc):
        if("{" in line):
            functionName += line.split("{")[0] + "{"
        else:
            functionName += line.split("{")[0]
        return functionName

    def grabScopeLine(self, functionName, line, lineType):
        return functionName

    #Add "{" from the new stack and update the functional and block caches accordingly
    def increaseNewBrackets(self, stackValue, line, changeType):
        if(changeType == GENERIC):
            for i in range(0, line.count("{")):
                self.newVerStack.append(("{", GENERIC))
        elif(changeType == FUNC):
            self.newVerStack.append((stackValue, FUNC))
            self.lastNewFuncContext = stackValue
        elif(changeType == SBLOCK): #Consider this carefully for when we get the opening {...
            self.newVerStack.append((stackValue, SBLOCK))
            self.lastNewBlockContext.append(stackValue)
        else:
            assert("Not a valid change type.")

    #Add "{" from the old stack and update the functional and block caches accordingly
    def increaseOldBrackets(self, stackValue, line, changeType):
        if(changeType == GENERIC):
            for i in range(0, line.count("{")):
                self.oldVerStack.append(("{", GENERIC))
        elif(changeType == FUNC):
            self.oldVerStack.append((stackValue, FUNC))
            self.lastOldFuncContext = stackValue
        elif(changeType == SBLOCK): #Consider this carefully for when we get the opening {...
            self.oldVerStack.append((stackValue, SBLOCK))
            self.lastOldBlockContext.append(stackValue)
        else:
            assert("Not a valid change type.")

    #string, [ADD|REMOVE|OTHER], [GENERIC|FUNC|BLOCK] -> --
    #Increase the depth of our tracker and add in function or block contexts if they have been discovered.
    #Note: LineNum is not used in this implementation.
    def increaseScope(self, stackValue, line, lineType, changeType, lineDiff = -1, isSimul = False):
        if(lineType == ADD):
            self.increaseNewBrackets(stackValue, line, changeType)
        elif(lineType == REMOVE):
            self.increaseOldBrackets(stackValue, line, changeType)
        elif(lineType == OTHER):
            self.increaseOldBrackets(stackValue, line, changeType)
            self.increaseNewBrackets(stackValue, line, changeType)
        else:
            assert("Not a valid line type")

    #Remove "}" from the new stack and update the functional and block caches accordingly
    def decreaseNewBrackets(self, line):
        for i in range(0, line.count("}")):
            if(self.newVerStack != []):
                removed = self.newVerStack.pop()
                if(self.config_info.DEBUG):
                    print("Removing: " + str(removed))
                    print("Context: " + str(self.lastNewBlockContext))
                if(removed[LABELINDEX] == FUNC):
                    self.lastNewFuncContext = self.getTopType(self.newVerStack, FUNC)
                elif(removed[LABELINDEX] == SBLOCK):
                    self.lastNewBlockContext.remove(removed[LINEINDEX])
            else:#Bracket overclosing -> estimating...
                if(self.config_info.DEBUG):
                    print("Popped from empty new Stack.")
                break

    #Remove "}" from the old stack and update the functional and block caches accordingly
    def decreaseOldBrackets(self, line):
        for i in range(0, line.count("}")):
            if(self.oldVerStack != []):
                removed = self.oldVerStack.pop()
                if(self.config_info.DEBUG):
                    print("Removing: " + str(removed))
                    print("Context: " + str(self.lastOldBlockContext))
                if(removed[LABELINDEX] == FUNC):
                    self.lastOldFuncContext = self.getTopType(self.oldVerStack, FUNC)
                elif(removed[LABELINDEX] == SBLOCK):
                    self.lastOldBlockContext.remove(removed[LINEINDEX])
            else:#Bracket overclosing -> estimating...
                if(self.config_info.DEBUG):
                    print("Popped from empty new Stack.")
                break

    #string, [ADD|REMOVE|OTHER] -> --
    #Decrease our current scope and close out any function or block contexts if necessary.
    def decreaseScope(self, line, lineType, lineDiff = -1, isSimul = False):
        if(lineType == ADD):
            self.decreaseNewBrackets(line)
        elif(lineType == REMOVE):
            self.decreaseOldBrackets(line)
        elif(lineType == OTHER):
            self.decreaseOldBrackets(line)
            self.decreaseNewBrackets(line)
        else:
            assert("Not a valid line type")

    def functionUpdateWithoutScopeChange(self, line, lineType, functionName, funcIdentFunc):
        raise NotImplementedError("Don't exist in Bracket Scope Tracker.")

    def changeScopeFirst(self):
        return False

    def afterDecrease(self, line):
        return line[line.find("}")+1:]

    def beforeDecrease(self, line):
        return line[:line.find("}")]

    def beforeIncrease(self, line):
        return line[:line.find("{")]

    def afterIncrease(self, line):
        return line[line.find("{")+1:]

    def adjustFunctionBorders(self, start, end, adds, deletes):
        return (start, end, adds, deletes)