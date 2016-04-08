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
class PythonScopeTracker(scopeTracker):
    def __init__(self, language):
        #These are pseudo stacks implemented as lists that track the current 
        #number of open scopes (brackets, tabs, etc), each change gets its own
        #entry, which is then deleted when we see a matching closing entry
        #Functions and blocks are included in full so they can be matched later
        self.oldVerStack = []
        self.newVerStack = []
        self.indentToken = "" #This tells us what the indent token for the file is.  Can be a number of spaces or tab
        self.funcNewLine = -1 #Did the last indentation contain a function name? (-1 is uninitialized)
        self.blockNewLine = 0 #Did the last indentation contain a block match?
        self.funcOldLine = -1 #Did the last indentation contain a function name? (-1 is uninitialized)
        self.blockOldLine = 0 #Did the last indentation contain a block match?
        self.newBlockKeyword = ""
        self.oldBlockKeyword = ""

        self.lastOldFuncContext = ""
        self.lastOldBlockContext = set()
        self.lastNewFuncContext = ""
        self.lastNewBlockContext = set()
        self.language = language

    #String -> list
    #Returns a list giving the sequence of scope changes in this line.
    def scopeOrder(self, line, lineType):
        if(self.isScopeIncrease(line,lineType)):
            return [INCREASE]
        elif(self.isScopeDecrease(line,lineType)):
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
        #if(Util.DEBUG):
        #    try:
        #        print("Indent Token: \"" + self.indentToken + "\"")
        #        print("WhiteSpace: \"" + whiteSpace + "\"")
        #    except:
        #        print("Indent Token: \"" + unicode(self.indentToken, 'utf-8', errors='ignore') + "\"")
        #        print("WhiteSpace: \"" + unicode(whiteSpace, 'utf-8', errors='ignore') + "\"")

        assert(self.indentToken != "")
        if(self.indentToken == "\t"):
            assert(" " not in whiteSpace)
        else:
            assert("\t" not in whiteSpace)

        return len(re.findall(self.indentToken, whiteSpace))

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
                    return len(self.newVerStack) < depth
                elif(lineType == REMOVE):
                    return len(self.oldVerStack) < depth
                elif(lineType == OTHER): #Can these be different?
                    return len(self.oldVerStack) < depth or len(self.newVerStack) < depth #If these are different, just adjust the stack accordingly
                else:
                    assert("Not a valid line type")
        else:
            return False

    #Returns true if this line contains an decreased level of scope.
    def isScopeDecrease(self, line, lineType):
        print("IN isScopeDecrease")
        print("Indent Token: \"" + self.indentToken + "\"")
        if(self.indentToken == ""): #If Scope is decreasing, if must have increased at some point
            return False

        indent = re.match(r"\s*", line).group() 
        depth = self.indentDepth(indent)
        print("Depth:" + str(depth))
        print("Line: \"" + line + "\"")
        print("Old Stack: " + str(self.oldVerStack))
        if(lineType == ADD):
            return len(self.newVerStack) > depth
        elif(lineType == REMOVE):
            return len(self.oldVerStack) > depth
        elif(lineType == OTHER): #Can these be different?
            return len(self.oldVerStack) > depth or len(self.newVerStack) > depth #If these are different, just adjust the stack accordingly
        else:
            assert("Not a valid line type")

    def handleFunctionNameEnding(self, line, functionName, lineType, funcIdentFunc):
        #Our job here is to distinguish between a indented line with a function def
        #and the indented line following the function.
        if(Util.DEBUG):
            print("Handle Ending")
            print("FunctionName: " + functionName)
            print("Line: " + line)
            print("Old Context:" + self.lastOldFuncContext)
            print("New Context:" + self.lastNewFuncContext)

        if(funcIdentFunc(functionName) != ""): #This is the line containing the followup
            #This is not returning the name correctly
            if(Util.DEBUG):
                print("1")
            if(lineType == ADD):
                self.funcNewLine = 1
                self.lastNewFuncContext = functionName #Double check these...
            elif(lineType == REMOVE):
                self.funcOldLine = 1
                self.lastOldFuncContext = functionName
            elif(lineType == OTHER):
                self.funcOldLine = 1
                self.funcNewLine = 1
                self.lastNewFuncContext = functionName
                self.lastOldFuncContext = functionName
            else:
                assert("Not a valid line type")

            return functionName
        elif(funcIdentFunc(functionName + " " + line) != ""): # This is the line containing the function
            if(Util.DEBUG):
                print("2")
            if(lineType == ADD):
                self.funcNewLine = 0
            elif(lineType == REMOVE):
                print("Changing Old Line to 0")
                self.funcOldLine = 0
            elif(lineType == OTHER):
                print("Changging Old Line to 0")
                self.funcNewLine = 0
                self.funcOldLine = 0
            else:
                 assert("Not a valid line type")
            return functionName + " " + line
        else:
            if(Util.DEBUG):
                print("3")
            if(lineType == ADD):
                self.funcNewLine = -1
            elif(lineType == REMOVE):
                self.funcOldLine = -1
            elif(lineType == OTHER):
                self.funcOldLine = -1
                self.funcNewLine = -1
            else:
                assert("Not a valid line type")

            return ""

    def grabScopeLine(self, functionName, line, lineType):
        if(lineType == ADD or lineType == OTHER):
            if(self.funcNewLine == 1):
                return(line)
            elif(self.funcNewLine == 0):
                return(functionName)
            else:
                assert("Parse error, if this is a function we should be either at it or the line following.")
        elif(lineType == REMOVE):
            if(self.funcOldLine == 1):
                return(line)
            elif(self.funcOldLine == 0):
                return(functionName)
            else:
                assert("Parse error, if this is a function we should be either at it or the line following.")
        else:
            assert("Not a valid line type")
        

    def increaseNewIndent(self, line, changeType, lineDiff):
        if(Util.DEBUG):
            print("New Indent Increase")
            print("Adding: " + str(line))
            print("Type: " + str(changeType))
            print("Stack: " + str(self.newVerStack))

        if(changeType == GENERIC):
            if(self.funcNewLine != 1 and self.blockNewLine == 0):
                self.newVerStack.append((self.indentToken, GENERIC)) #Should be able to increase only 1 level at a time?
            elif(self.blockNewLine == 1):
                assert(self.funcNewLine != 1)
                assert(self.newBlockKeyword != "")
                self.newVerStack.append((self.newBlockKeyword, SBLOCK))
                self.lastNewBlockContext.add(self.newBlockKeyword)
                self.blockNewLine = 0
                self.newBlockKeyword = ""
            else: # This is actually the indentation after a function that was also idented.
                self.newVerStack.append((self.lastNewFuncContext, FUNC))
                self.funcNewLine = -1  #Reset after the handle function.
        elif(changeType == FUNC):
            #Mark that we've seen the function... 
            if(self.funcNewLine == 0): #Func line that is indented
                self.newVerStack.append((self.indentToken, GENERIC))
                self.lastNewFuncContext = line
                self.funcNewLine = 1
            elif(self.funcNewLine == 1): #Indent after a func line, outside code would've passed the func name here after a match.
                self.newVerStack.append((self.lastNewFuncContext, FUNC))
                self.funcNewLine = -1  #Reset after the handle function.
            else:
                assert("Parse error.  Scope tracker expected a FUNC tag.")
        elif(changeType == SBLOCK):
            if(lineDiff == 0): #This is not the indent for the Block, but a Block keyword that is indented
                self.blockNewLine = 1
                self.newBlockKeyword = line
                self.newVerStack.append((self.indentToken, GENERIC))
            elif(lineDiff == 1): #Indent after a Block line.
                self.newVerStack.append((line, SBLOCK))
                self.lastNewBlockContext.add(line)
        else:
            assert("Not a valid change type.")

        if(Util.DEBUG):
            print("Stack (After): " + str(self.newVerStack))

    def increaseOldIndent(self, line, changeType, lineDiff):
        if(Util.DEBUG):
            print("Old Indent Increase")
            print("Adding: " + str(line))
            print("Type: " + str(changeType))
            print("Stack: " + str(self.oldVerStack))

        if(changeType == GENERIC):
            print("GENERIC!")
            print("Func Old Line: " + str(self.funcOldLine))
            print("Block Old Line: " + str(self.blockOldLine))
            if(self.funcOldLine != 1 and self.blockOldLine == 0):
                self.oldVerStack.append((self.indentToken, GENERIC)) #Should be able to increase only 1 level at a time?
            elif(self.blockOldLine == 1):
                assert(self.oldBlockKeyword != "")
                self.oldVerStack.append((self.oldBlockKeyword, SBLOCK))
                self.lastOldBlockContext.add(self.oldBlockKeyword)
                self.blockOldLine = 0
                self.oldBlockKeyword = ""
            else: # This is actually the indentation after a function that was also idented.
                self.oldVerStack.append((self.lastOldFuncContext, FUNC))
                self.funcOldLine = -1  #Reset after the handle function.
        elif(changeType == FUNC):
            #Mark that we've seen the function... 
            if(self.funcOldLine == 0): #Func line that is indented
                print("Changing Old Line to 1")
                self.oldVerStack.append((self.indentToken, GENERIC))
                self.lastOldFuncContext = line
                self.funcOldLine = 1
                print("Func Old Line: " + str(self.funcOldLine))
            elif(self.funcOldLine == 1): #Indent after a func line
                self.oldVerStack.append((self.lastOldFuncContext, FUNC))
                self.funcOldLine = -1  
            else:
                assert("Parse error.  Scope tracker expected a FUNC tag.")

        elif(changeType == SBLOCK):
            if(lineDiff == 0): #This is not the indent for the Block, but a Block keyword that is indented
                self.blockOldLine = 1
                self.oldBlockKeyword = line
                self.oldVerStack.append((self.indentToken, GENERIC))
            elif(lineDiff == 1): #Indent after a Block line.
                self.oldVerStack.append((line, SBLOCK))
                self.lastOldBlockContext.add(line)
        else:
            assert("Not a valid change type.")

        if(Util.DEBUG):
            print("Stack (After): " + str(self.oldVerStack))

    #string, [ADD|REMOVE|OTHER], [GENERIC|FUNC|BLOCK] -> --
    #Increase the depth of our tracker and add in function or block contexts if they have been discovered.
    def increaseScope(self, line, lineType, changeType, lineDiff = -1):
        if(Util.DEBUG): 
            try:
                print("Scope Increasing Line: " + line)
            except:
                print("Scope Increasing Line: " + unicode(line, 'utf-8', errors='ignore'))

        if(lineType == ADD):
            self.increaseNewIndent(line, changeType, lineDiff)
        elif(lineType == REMOVE):
            self.increaseOldIndent(line, changeType, lineDiff)
        elif(lineType == OTHER): 
            #TODO: How do I handle this now.
            #If increase relative to old th
            depth = self.indentDepth(line)
            isOldIncrease = len(self.oldVerStack) < depth
            isNewIncrease = len(self.newVerStack) < depth
            if(isOldIncrease):
                self.increaseOldIndent(line, changeType, lineDiff)
            if(isNewIncrease):
                self.increaseNewIndent(line, changeType, lineDiff)
        else:
            assert("Not a valid line type")


    #Remove indents from the new stack and update the functional and block caches accordingly
    def decreaseNewIndent(self, line):
        if(self.newVerStack != []):
            removed = self.newVerStack.pop()
            if(Util.DEBUG):
                print("Removing: " + str(removed))
                print("Context: " + str(self.lastNewBlockContext))
                print("Stack: " + str(self.newVerStack))
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
                print("Stack: " + str(self.oldVerStack))
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
            self.decreaseNewIndent(line)
        elif(lineType == REMOVE):
            self.decreaseOldIndent(line)
        elif(lineType == OTHER): 
            #TODO: How do I handle this now.
            #If increase relative to old th
            depth = self.indentDepth(line)
            isOldDecrease = len(self.oldVerStack) > depth
            isNewDecrease = len(self.newVerStack) > depth
            if(isOldDecrease):
                self.decreaseOldIndent(line)
            if(isNewDecrease):
                self.decreaseNewIndent(line)
        else:
            assert("Not a valid line type")

    def decreaseScopeFirst(self):
        return True

    def beforeDecrease(self, line): #A decrease always happens at the start of a line, so return nothing.
        return ""

    def afterIncrease(self, line): #No need to do anything here. We can't have code before the indentation.
        return line