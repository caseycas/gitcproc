import sys
import re

sys.path.append("../util")

import Util
import UnsupportedLanguageException
from UnsupportedScopeException import *
from chunkingConstants import *
from scopeTracker import *

#Scope Tracking in Python
#Can not mix Tabs and WhiteSpaces
#Indent level not specific


#Redo with a polymorphic solution for the languages
class PythonScopeTracker(scopeTracker):
    def __init__(self, language, c_info):
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
        #self.lastOldBlockContext = []
        self.lastNewFuncContext = ""
        #self.lastNewBlockContext = []
        self.language = language
        self.isContinuation = NOT_CONTINUATION
        self.shiftStart = False
        self.startType = OTHER
        self.config_info = c_info

    #String -> list
    #Returns a list giving the sequence of scope changes in this line.
    #TODO: Update me!
    def scopeOrder(self, line, lineType):
        incVal = self.isScopeIncrease(line,lineType)
        decVal = self.isScopeDecrease(line,lineType)
        if(incVal == S_YES):
            return [INCREASE]
        elif(decVal == S_YES):
            return [DECREASE] #Report all numbers of scope decreases equally.
        elif(incVal == S_SIMUL or decVal == S_SIMUL):
            if(self.config_info.DEBUG):
                print(incVal)
                print(decVal)
            #assert(decVal == S_SIMUL) #This isn't true necessarily
            return [S_SIMUL]
        else:
            return []
        
    def scopeIncreaseCount(self, line, lineType):
        if(self.isScopeIncrease(line,lineType) in [S_YES, S_SIMUL]):
            return 1
        else:
            return 0

    def scopeDecreaseCount(self, line, lineType):
        if(self.isScopeDecrease(line, lineType) in [S_YES, S_SIMUL]):
            return 1
        else:
            return 0

    def indentDepth(self, whiteSpace):
        #Make sure there is no mixing of tabs and spaces
        if(self.config_info.DEBUG):
            try:
                print("Indent Token: \"" + self.indentToken + "\"")
                print("WhiteSpace: \"" + whiteSpace + "\"")
            except:
                print("Indent Token: \"" + unicode(self.indentToken, 'utf-8', errors='ignore') + "\"")
                print("WhiteSpace: \"" + unicode(whiteSpace, 'utf-8', errors='ignore') + "\"")

        assert(self.indentToken != "")
        if(self.indentToken == "\t"): 
            if(" " in whiteSpace):
                raise UnsupportedScopeException("Spaces found in tab indented python file.")
            #assert(" " not in whiteSpace) #Make an error for this...
        else: #I have discovered real code that is mixing these, let's try replace tabs with spaces....
            #assert("\t" not in whiteSpace)
            if("\t" in whiteSpace):
                #I don't know if this is technically correct, but the code shouldn't be doing this anyway.
                #I'm looking at you ansible
                whiteSpace.replace("\t",self.indentToken) 
                #whiteSpace.replace("\t","        ") #I think tabs are replaced by 8 spaces... 

        return len(re.findall(self.indentToken, whiteSpace))

    #Returns true if this line contains an increased level of scope.
    #One possible concern here is a single statement spread over multiple lines.  I don't think that would cause
    #issues if we treat them like any other indent, but it could be a problem.
    def isScopeIncrease(self, line, lineType):
        if(self.isContinuation in [CONTINUATION, CONTINUATION_END,CONTINUATION_EXPLICIT]): #Ignore Scope changes from continuation lines.
            return S_NO
        #Match beginning whitespace.  Credit to kennytm here: 
        #http://stackoverflow.com/questions/2268532/grab-a-lines-whitespace-indention-with-python
        indent = re.match(r"\s*", line).group() 
        if(indent != ""):
            if(self.indentToken == ""): #Is this the first indent in the file?  Use this to determine future indentation
                self.indentToken = indent
                return S_YES
            else:
                #How deep is the indent?
                depth = self.indentDepth(indent)
                if(lineType == ADD):
                    if(len(self.newVerStack) < depth):
                        return S_YES
                elif(lineType == REMOVE):
                    if(len(self.oldVerStack) < depth):
                        return S_YES
                elif(lineType == OTHER): #Can these be different?
                    oldDiff = len(self.oldVerStack) < depth
                    newDiff = len(self.newVerStack) < depth 
                    if(oldDiff != newDiff): #Scope is decreasing from the perspective of one stack and increasing from the other.
                        return S_SIMUL
                    elif(oldDiff == True):
                        return S_YES
                    else:
                        return S_NO
                else:
                    assert("Not a valid line type")
        else:
            return S_NO

    #Returns true if this line contains an decreased level of scope.
    def isScopeDecrease(self, line, lineType):
        if(self.config_info.DEBUG):
            print("IN isScopeDecrease")
            print("Indent Token: \"" + self.indentToken + "\"")
            print("Line: \"" + line + "\"")
        if(self.indentToken == ""): #If Scope is decreasing, if must have increased at some point
            return S_NO
        #We need to ignore blank lines for scope Decreases?
        if(line == ""):
            return S_NO

        if(self.isContinuation in [CONTINUATION, CONTINUATION_END, CONTINUATION_EXPLICIT]): #Ignore Scope changes from continuation lines.
            return S_NO

        indent = re.match(r"\s*", line).group() 
        depth = self.indentDepth(indent)
        if(self.config_info.DEBUG):
            print("Depth:" + str(depth))
            print("Line: \"" + line + "\"")
            print("Old Stack: " + str(self.oldVerStack))
        if(lineType == ADD):
            if(len(self.newVerStack) > depth):
                return S_YES
        elif(lineType == REMOVE):
            if(len(self.oldVerStack) > depth):
                return S_YES
        elif(lineType == OTHER): #Can these be different?
            oldDiff = len(self.oldVerStack) > depth
            newDiff = len(self.newVerStack) > depth
            if(self.config_info.DEBUG):
                print("Old Diff:" + str(oldDiff))
                print("New Diff:" + str(newDiff))
            if(oldDiff != newDiff): #Scope is decreasing from the perspective of one stack and increasing from the other.
                return S_SIMUL
            elif(oldDiff == True):
                return S_YES
            else:
                return S_NO
        else:
            assert("Not a valid line type")

    def isFunctionalScopeChange(self, line, lineType):
        return (self.isScopeIncrease(line, lineType) or self.isScopeDecrease(line, lineType))


    def functionUpdateWithoutScopeChange(self, line, lineType, functionName, funcIdentFunc):
        """
        Goal here is track if we've seen a complete function pattern, but without an indent increase on the
        function line itself.  (Thought:  Maybe need to do this on a scope decrease as well.)
        """
        if(funcIdentFunc(functionName + " " + line) != ""):
            if(self.config_info.DEBUG):
                print("Function Name Found before scope INCREASE")
            if(lineType == ADD):
                self.funcNewLine = 1
                self.lastNewFuncContext = functionName + " " + line #Double check these...
            elif(lineType == REMOVE):
                self.funcOldLine = 1
                self.lastOldFuncContext = functionName + " " + line
            elif(lineType == OTHER):
                #TODO: Something about these flags may need to change in SIMUL?
                #Actually possibly not, because this is only called on a S_NO
                self.funcOldLine = 1
                self.funcNewLine = 1
                self.lastNewFuncContext = functionName + " " + line
                self.lastOldFuncContext = functionName + " " + line
            else:
                assert("Not a valid line type")



    def handleFunctionNameEnding(self, line, functionName, lineType, funcIdentFunc):
        #Our job here is to distinguish between a indented line with a function def
        #and the indented line following the function.
        #What if we have a class name?
        #TODO: In Simul cases, I don't think this function is behaving correctly, its non
        #increase counterpart is likely also not behaving correctly.
        if(self.config_info.DEBUG):
            print("Handle Ending")
            print("FunctionName: " + functionName)
            print("Line: " + line)
            print("Old Context:" + self.lastOldFuncContext)
            print("New Context:" + self.lastNewFuncContext)

        if(funcIdentFunc(functionName) != ""): #This is the line containing the followup
            if(self.config_info.DEBUG):
                print("1")
            if(lineType == ADD):
                self.funcNewLine = 1
                self.lastNewFuncContext = functionName #Double check these...
            elif(lineType == REMOVE):
                self.funcOldLine = 1
                self.lastOldFuncContext = functionName
            elif(lineType == OTHER):
                #TODO:Something about these flags needs to be different for SIMUL I think...
                self.funcOldLine = 1
                self.funcNewLine = 1
                self.lastNewFuncContext = functionName
                self.lastOldFuncContext = functionName
            else:
                assert("Not a valid line type")

            return functionName
        elif(funcIdentFunc(functionName + " " + line) != ""): # This is the line containing the function
            #Issue is that we are counting this line as the function start in this case
            self.shiftStart = True
            self.startType = lineType
            if(self.config_info.DEBUG):
                print("2")
            if(lineType == ADD):
                if(self.config_info.DEBUG):
                    print("Changing function new Line to 0")
                self.funcNewLine = 0
            elif(lineType == REMOVE):
                if(self.config_info.DEBUG):
                    print("Changing function Old Line to 0")
                self.funcOldLine = 0
            elif(lineType == OTHER):
                if(self.config_info.DEBUG):
                    print("Changing function Old and New Line to 0")
                #TODO:Something about these flags needs to be different for SIMUL I think...
                self.funcNewLine = 0
                self.funcOldLine = 0
            else:
                 assert("Not a valid line type")
            return functionName + " " + line
        else: #This is not a function
            if(self.config_info.DEBUG):
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

    #Handle the scope change for a line where we have difference kinds of scope changes
    #depending on if you are measuring from the old stack or the new stack.
    #This covers the following cases:
    #1. Increase relative to old, Decrease relative to new 
    #2. Increase relative to old, no change with new
    #3. No change to old, decrease relative to new
    #4. No change to old, increase relative to new
    #5. Decrease relative to old, no change with new
    #6. Decrease relative to old, increase relative to new
    def simulScopeChange(self, stackValue, lineType, changeType, depth, lineDiff):
            #Error, in that this isn't behaving correctly in 3, 5? when there's a block keyword on the line...
            oldChange = len(self.oldVerStack) - depth
            newChange = len(self.newVerStack) - depth
            #if(not ((oldChange < 0 and newChange > 0) or (oldChange > 0 and newChange < 0))):
            if(self.config_info.DEBUG):
                print("SIMUL SCOPE CHANGE:")
                print("Line: " + stackValue)
                print("Depth: " + str(depth))
                print("OldChange: " + str(oldChange))
                print("NewChange: " + str(newChange))
                print("Func Old Line: " + str(self.funcOldLine))
                print("Func New Line: " + str(self.funcNewLine))
                print("Block Old Line: " + str(self.blockOldLine))
                print("Block New Line: " + str(self.blockNewLine))
                print("Arguments: " + " ".join([str(stackValue), str(lineType), str(changeType), str(depth), str(lineDiff)]))
                print("STACKVALUES")
                self.printScope()
            #    #assert(0)
            if(oldChange > 0):
                while(oldChange > 0):
                    oldChange -= 1
                    self.decreaseOldIndent()
            elif(oldChange < 0):
                if(oldChange != -1):
                    raise UnsupportedScopeException("Python scope increased by more than 1")
                #assert(oldChange == -1) #Only permitted one increase at a time.
                #This needs to be tuned for a block or func change
                #if(funcOldLine != -1):
                #    self.increaseOldIndent(stackValue, FUNC, lineDiff)
                #elif(Block)
                self.increaseOldIndent(stackValue, changeType, lineDiff) #TODO lineDiff = ??
            if(newChange > 0):
                while(newChange > 0):
                    newChange -= 1
                    self.decreaseNewIndent()
            elif(newChange < 0):
                if(newChange != -1):
                    raise UnsupportedScopeException("Python scope increased by more than 1")
                #assert(newChange == -1) #Only permitted one increase at a time.
                #This needs to be tuned for a block or func change
                self.increaseNewIndent(stackValue, changeType, lineDiff) #TODO lineDiff = ??

            #if(not ((oldChange < 0 and newChange > 0) or (oldChange > 0 and newChange < 0))):
            if(self.config_info.DEBUG):
                print("SIMUL SCOPE CHANGE:")
                print("STACKVALUES")
                self.printScope()


    def increaseNewIndent(self, stackValue, changeType, lineDiff):
        if(self.config_info.DEBUG):
            print("New Indent Increase")
            print("Adding: " + str(stackValue))
            print("Type: " + str(changeType))
            print("Stack: " + str(self.newVerStack))

        if(changeType == GENERIC):
            if(self.funcNewLine != 1 and self.blockNewLine == 0):
                self.newVerStack.append((self.indentToken, GENERIC)) #Should be able to increase only 1 level at a time?
            elif(self.blockNewLine == 1):
                assert(self.funcNewLine != 1)
                assert(self.newBlockKeyword != "")
                self.newVerStack.append((self.newBlockKeyword, SBLOCK))
                #self.lastNewBlockContext.append(self.newBlockKeyword)
                self.blockNewLine = 0
                self.newBlockKeyword = ""
            else: # This is actually the indentation after a function that was also idented.
                self.newVerStack.append((self.lastNewFuncContext, FUNC))
                self.funcNewLine = -1  #Reset after the handle function.
        elif(changeType == FUNC):
            #Mark that we've seen the function... 
            if(self.funcNewLine == 0): #Func line that is indented
                self.newVerStack.append((self.indentToken, GENERIC))
                self.lastNewFuncContext = stackValue
                self.funcNewLine = 1
            elif(self.funcNewLine == 1): #Indent after a func line, outside code would've passed the func name here after a match.
                self.newVerStack.append((self.lastNewFuncContext, FUNC))
                self.funcNewLine = -1  #Reset after the handle function.
            else:
                assert("Parse error.  Scope tracker expected a FUNC tag.")
        elif(changeType == SBLOCK):
            if(lineDiff == 0): #This is not the indent for the Block, but a Block keyword that is indented
                self.blockNewLine = 1
                self.newBlockKeyword = stackValue
                #self.lastNewBlockContext.append(line)
                if(self.funcNewLine == 1): #Update to store the function on the stack if it was waiting to be added
                    self.newVerStack.append((self.lastNewFuncContext, FUNC))
                    self.funcNewLine = -1  #Reset after the handle function.
                else:
                    self.newVerStack.append((self.indentToken, GENERIC))
            elif(lineDiff == 1): #Indent after a Block line.
                self.blockNewLine = 0
                self.newVerStack.append((stackValue, SBLOCK))
                #self.lastNewBlockContext.append(line)
        else:
            assert("Not a valid change type.")

        if(self.config_info.DEBUG):
            print("Stack (After): " + str(self.newVerStack))

    def increaseOldIndent(self, stackValue, changeType, lineDiff):
        if(self.config_info.DEBUG):
            print("Old Indent Increase")
            print("Adding: " + str(stackValue))
            print("Type: " + str(changeType))
            print("Stack: " + str(self.oldVerStack))

        if(changeType == GENERIC):
            if(self.config_info.DEBUG):
                print("GENERIC!")
                print("Func Old Line: " + str(self.funcOldLine))
                print("Block Old Line: " + str(self.blockOldLine))
            if(self.funcOldLine != 1 and self.blockOldLine == 0):
                self.oldVerStack.append((self.indentToken, GENERIC)) #Should be able to increase only 1 level at a time?
            elif(self.blockOldLine == 1):
                assert(self.oldBlockKeyword != "")
                self.oldVerStack.append((self.oldBlockKeyword, SBLOCK))
                #self.lastOldBlockContext.append(self.oldBlockKeyword)
                self.blockOldLine = 0
                self.oldBlockKeyword = ""
            else: # This is actually the indentation after a function that was also idented.
                self.oldVerStack.append((self.lastOldFuncContext, FUNC))
                self.funcOldLine = -1  #Reset after the handle function.
        elif(changeType == FUNC):
            #Mark that we've seen the function... 
            if(self.funcOldLine == 0): #Func line that is indented
                if(self.config_info.DEBUG):
                    print("Changing Old Line to 1")
                self.oldVerStack.append((self.indentToken, GENERIC))
                self.lastOldFuncContext = stackValue
                self.funcOldLine = 1
                if(self.config_info.DEBUG):
                    print("Func Old Line: " + str(self.funcOldLine))
            elif(self.funcOldLine == 1): #Indent after a func line
                self.oldVerStack.append((self.lastOldFuncContext, FUNC))
                self.funcOldLine = -1  
            else:
                assert("Parse error.  Scope tracker expected a FUNC tag.")

        elif(changeType == SBLOCK):
            if(lineDiff == 0): #This is not the indent for the Block, but a Block keyword that is indented
                self.blockOldLine = 1
                self.oldBlockKeyword = stackValue
                if(self.funcOldLine == 1): #Update to store the function on the stack if it was waiting to be added
                    self.oldVerStack.append((self.lastOldFuncContext, FUNC))
                    self.funcOldLine = -1  #Reset after the handle function.
                else:
                    self.oldVerStack.append((self.indentToken, GENERIC))
                #self.lastOldBlockContext.append(line)
            elif(lineDiff == 1): #Indent after a Block line.
                self.blockOldLine = 0
                self.oldVerStack.append((stackValue, SBLOCK))
                #self.lastOldBlockContext.append(line)
        else:
            assert("Not a valid change type.")

        if(self.config_info.DEBUG):
            print("Stack (After): " + str(self.oldVerStack))

    #string, [ADD|REMOVE|OTHER], [GENERIC|FUNC|BLOCK] -> --
    #Increase the depth of our tracker and add in function or block contexts if they have been discovered.
    #Error when doing a block, we have sent just the keyword. We need the whole line for the unmodified version....
    def increaseScope(self, stackValue, line, lineType, changeType, lineDiff = -1, isSimul = False):
        if(self.config_info.DEBUG): 
            try:
                print("Scope Increasing Line: " + line)
            except:
                print("Scope Increasing Line: " + unicode(line, 'utf-8', errors='ignore'))

        if(lineType == ADD):
            self.increaseNewIndent(stackValue, changeType, lineDiff)
        elif(lineType == REMOVE):
            self.increaseOldIndent(stackValue, changeType, lineDiff)
        elif(lineType == OTHER): # Need to handle this differently in case of a SIMUL
            depth = self.indentDepth(line)
            if(isSimul):
                self.simulScopeChange(stackValue, lineType, changeType, depth, lineDiff)
            else:
                isOldIncrease = len(self.oldVerStack) < depth
                isNewIncrease = len(self.newVerStack) < depth
                if(isOldIncrease):
                    self.increaseOldIndent(stackValue, changeType, lineDiff)
                if(isNewIncrease):
                    self.increaseNewIndent(stackValue, changeType, lineDiff)
        else:
            assert("Not a valid line type")


    #Remove indents from the new stack and update the functional and block caches accordingly
    def decreaseNewIndent(self):
        if(self.newVerStack != []):
            removed = self.newVerStack.pop()
            if(self.config_info.DEBUG):
                print("Removing: " + str(removed))
                #print("Context: " + str(self.lastNewBlockContext))
                print("Stack: " + str(self.newVerStack))
            if(removed[LABELINDEX] == FUNC):
                self.lastNewFuncContext = self.getTopType(self.newVerStack, FUNC)
            #elif(removed[LABELINDEX] == SBLOCK):
            #    self.lastNewBlockContext.remove(removed[LINEINDEX])
        else:#Bracket overclosing -> estimating...
            if(self.config_info.DEBUG):
                print("Popped from empty new Stack.")

    #Remove indents from the old stack and update the functional and block caches accordingly
    def decreaseOldIndent(self):
        if(self.oldVerStack != []):
            removed = self.oldVerStack.pop()
            if(self.config_info.DEBUG):
                print("Removing: " + str(removed))
                #print("Context: " + str(self.lastOldBlockContext))
                print("Stack: " + str(self.oldVerStack))
            if(removed[LABELINDEX] == FUNC):
                self.lastOldFuncContext = self.getTopType(self.oldVerStack, FUNC)
            #elif(removed[LABELINDEX] == SBLOCK):
                #self.lastOldBlockContext.remove(removed[LINEINDEX])
                #print("Current block context: " + str(self.lastOldBlockContext))
        else:#Bracket overclosing -> estimating...
            if(self.config_info.DEBUG):
                print("Popped from empty old Stack.")

    #string, [ADD|REMOVE|OTHER] -> --
    #Decrease our current scope and close out any function or block contexts if necessary.
    def decreaseScope(self, line, lineType, lineDiff = -1, isSimul = False):
        #We are allowed to decrease the scope by how ever much we want
        depth = self.indentDepth(line)
        if(lineType == ADD):
            decreases = len(self.newVerStack) - depth
            while(decreases > 0):
                decreases -= 1
                self.decreaseNewIndent()
        elif(lineType == REMOVE):
            decreases = len(self.oldVerStack) - depth
            while(decreases > 0):
                decreases -= 1
                self.decreaseOldIndent()
        elif(lineType == OTHER):
            if(isSimul):
                #NOTE: Generic may not be correct here, observe behavior carefully.
                self.simulScopeChange(line, lineType, GENERIC, depth, lineDiff)
            else:
                oldDecreases = len(self.oldVerStack) - depth
                newDecreases = len(self.newVerStack) - depth
                while(oldDecreases > 0):
                    oldDecreases -= 1
                    self.decreaseOldIndent()
                while(newDecreases > 0):
                    newDecreases -= 1
                    self.decreaseNewIndent()
        else:
            assert("Not a valid line type")

    def changeScopeFirst(self):
        return True

    def adjustFunctionBorders(self, start, end, adds, deletes):
        if(self.shiftStart):
            self.shiftStart = False
            if(self.startType == ADD):
                return (start - 1, end, adds - 1 , deletes)
            elif(self.startType == REMOVE):
                return (start - 1, end, adds , deletes - 1)
            elif(self.startType == OTHER):
                return (start - 1, end, adds, deletes)
            else:
                assert("Invalid line type.")
        else:
            return (start, end, adds, deletes)

    def getBlocksFromStack(self, stack):
        subList = []
        for item in stack:
            if(item[LABELINDEX] == SBLOCK):
                subList.append(item[LINEINDEX])

        return subList


    #Return the surrounding block contexts or [] if not on the stack
    def getBlockContext(self, lineType):
        if(lineType == ADD or lineType == OTHER):
            return self.getBlocksFromStack(self.newVerStack)
        elif(lineType == REMOVE):
            return self.getBlocksFromStack(self.oldVerStack)
        else:
            assert("Not a valid line type")

    def getFuncFromStack(self, stack):
        for item in stack:
            if(item[LABELINDEX] == FUNC):
                return item[LINEINDEX]

        return ""

    def getFuncContext(self, lineType):
        if(lineType == ADD or lineType == OTHER):
            if(self.lastNewFuncContext != ""):
                return self.lastNewFuncContext
            elif(self.lastOldFuncContext != ""):
                return self.lastOldFuncContext
            else:
                return self.getFuncFromStack(self.newVerStack)
        elif(lineType == REMOVE):
            if(self.lastOldFuncContext != ""):
                return self.lastOldFuncContext
            elif(self.lastNewFuncContext != ""):
                return self.lastNewFuncContext
            else:
                return self.getFuncFromStack(self.oldVerStack)
        else:
            assert("Not a valid line type")


    def afterDecrease(self, line): #A decrease always happens at the start of a line, so return nothing.
        return line

    def beforeDecrease(self, line): #A decrease always happens at the start of a line, so return nothing.
        return ""

    def beforeIncrease(self, line): #No need to do anything here. We can't have code before the indentation.
        return ""

    def afterIncrease(self, line): #No need to do anything here. We can't have code before the indentation.
        return line

    def printScope(self):
        print("------------------<Scope Obj>------------------")
        print("Language:")
        print(self.language)
        print("Old Stack:")
        print(self.oldVerStack)
        print("Old Func Cache:")
        print(self.lastOldFuncContext)
        print("Old Block Keyword:")
        print(self.oldBlockKeyword)
        print("New Stack:")
        print(self.newVerStack)
        print("New Func Cache:")
        print(self.lastNewFuncContext)
        print("New Block Keyword:")
        print(self.newBlockKeyword)
        print("------------------<Scope Obj>------------------")