import re
import languageSwitcher
from InvalidCodeException import *

#How to combine these?
PythonFunctionPatterns = [" *def +[A-Za-z_]+[\w]*\(.*\): *$"]

PythonBlockComments = ["\"\"\"", "\"\"\""] #Problem, Can be ''' or """
PythonBlockComments2 = ["\'\'\'", "\'\'\'"]
PythonSingleComment = ["#"]

PythonCommentPatterns = ["\"\"\".*\"\"\"", "\'\'\'.*\'\'\'"]
PythonCommentPattern2 = "#.*"

PythonStringPattern = "\".*?\""
PythonStringPattern2 = "\'.*?\'"

#Regex to match to see if we should expect the next line to be a continuation line
#This can happen if we are in between (), {}, or [], or with an explicit \
PythonExplicitContinuationRegex = ".*\\\\ *"

#Potential Regexes to fill in based on the others.

#Formal definition of Python identifiers
#identifier ::=  (letter|"_") (letter | digit | "_")*
#letter     ::=  lowercase | uppercase
#lowercase  ::=  "a"..."z"
#uppercase  ::=  "A"..."Z"
#digit      ::=  "0"..."9"


PythonClassPatterns = [" class +[A-Za-z_]+[\w]* *\([\w. ]*\): *$", "^class +[A-Za-z_]+[\w]* *\([\w. ]*\): *$"]
PythonValidClassNamePattern = "[A-Za-z_]+[\w]*"
PythonParamPattern = "*\([\w\d_=,\[\]\(\) ]*\):"

PythonConstDestrRegex = "__init__|__del__+ "



class PythonLanguageSwitcher(languageSwitcher.languageSwitcher):
    #Do not call this constructor outside of the Factory
    def __init__(self, ext):
        super(PythonLanguageSwitcher, self).__init__(ext)
        self.lang = "Python"


    def isObjectOrientedLanguage(self):
        return True

    def getFunctionRegexes(self):
        return PythonFunctionPatterns
        
    def cleanFunctionLine(self, line):
        temp = line.replace("\n", "")
        temp = temp.replace("\r", "")
   
        return temp

    def cleanClassLine(self, line):
        return line.strip().lower().replace("\n", "")

    def getClassRegexes(self):
        return PythonClassPatterns

    def isValidClassName(self, classContext):
        return re.search(PythonValidClassNamePattern, classContext)

    def cleanConstructorOrDestructorLine(self, line):
        return line

    def shortenConstructorOrDestructor(self, toShorten):
        return toShorten

    def getConstructorOrDestructorRegex(self, classContext):
        #In python these are __init__ and __del__ they don't really need to be
        #treated as special cases, (so they won't fall through to here), but we should
        #have the ability to handle them if they fall through.
        return PythonConstDestrRegex + PythonParamPattern

    def parseFunctionName(self, fullName):
        #def name(): #I think it should be fine to return what falls in between the def and the first "("
        defLoc = fullName.find("def")
        name = fullName[defLoc:]
        increaseIndicies = [next.start() for next in re.finditer('\(', name)]
        
        if(defLoc == -1):
            raise ValueError("1. Function Name to parse is malformed.", fullName)
        if(len(increaseIndicies) == 0):
            raise ValueError("2. Function Name to parse is malformed.", fullName)
        #if(defLoc >= increaseIndicies[0]):
        #    raise ValueError("3. Function Name to parse is malformed.", fullName)

        return name[:increaseIndicies[0]].split(" ")[-1]

    def getBlockCommentStart(self, line):
        start = line.find(PythonBlockComments[0])
        if(start == -1):
            start = line.find(PythonBlockComments2[0])

        return start

    def getBlockCommentEnd(self, line):
        end = line.find(PythonBlockComments[1])
        if(end == -1):
            end = line.find(PythonBlockComments2[1])

        return end

    def isBlockCommentStart(self, line):
        return(line.find(PythonBlockComments[0]) != -1 or line.find(PythonBlockComments2[0]) != -1)

    def isBlockCommentEnd(self, line):
        return(line.find(PythonBlockComments[1]) != -1 or line.find(PythonBlockComments2[1]) != -1)

    def beforeBlockCommentStart(self, line):
        start = line.find(PythonBlockComments[0])
        if(start == -1):
            start = line.find(PythonBlockComments2[0])

        if(start == -1):
            return line
        else:
            return line[:start]
   
    def afterBlockCommentEnd(self, line):
        end = line.find(PythonBlockComments[1])
        if(end == -1):
            end = line.find(PythonBlockComments2[1])

        if(end == -1):
            return line
        else:
            return line[end + len(PythonBlockComments[1]):]


    def getSingleComment(self):
        return PythonSingleComment

    def cleanSingleLineBlockComment(self, line):
        return re.sub(PythonCommentPatterns[1], "",re.sub(PythonCommentPatterns[0], "", line))

    def cleanSingleLineComment(self, line):
        return re.sub(PythonCommentPattern2, "", line)

    def checkForFunctionReset(self, line):
        return False

    #Reset the function name after we have identified a scope change.
    def resetFunctionName(self, line):
        return line

    def clearFunctionRemnants(self,line):
        #return line.strip() #Remove indentation so we don't process further scope changes
        return line

    def isContinuationLine(self, line, priorStatus):
        """
        In Python a line counts as a continuation line under two circumstances - explicit and implicit.
        Explicit continuation lines must end in \
        Implicit continuation lines must have a Start in a ( or { or [ but have not match at the end.
        """
        if(line.strip() == ""):
            return priorStatus

        if(re.search(PythonExplicitContinuationRegex, line) != None):
            return languageSwitcher.CONTINUATION_EXPLICIT
        else: #Check if this is an implicit continuation
            BracketStack = []
            for char in line:
                if(char in "{[("):
                    BracketStack.append(char)
                elif(char == "}"):
                    if(BracketStack != [] and (BracketStack[-1] == "(" or BracketStack[-1] == "[")):
                        raise InvalidCodeException("Brackets: {} did not match in the code.")
                    elif(BracketStack != [] and BracketStack[-1] == "{"):
                        BracketStack.pop()
                    else:
                        BracketStack.append(char)     
                elif(char == "]"):
                    if(BracketStack != [] and (BracketStack[-1] == "(" or BracketStack[-1] == "{")):
                        raise InvalidCodeException("Braces: [] did not match in the code.")
                    elif(BracketStack != [] and BracketStack[-1] == "["):
                        BracketStack.pop()
                    else:
                        BracketStack.append(char)         
                elif(char == ")"):
                    if(BracketStack != [] and  (BracketStack[-1] == "{" or BracketStack[-1] == "[")):
                        raise InvalidCodeException("Parantheses: () did not match in the code.")
                    elif(BracketStack != [] and BracketStack[-1] == "("):
                        BracketStack.pop()
                    else:
                        BracketStack.append(char) 

            if(BracketStack == []):
                if(priorStatus in [languageSwitcher.CONTINUATION, languageSwitcher.CONTINUATION_START]):
                    return languageSwitcher.CONTINUATION
                else:
                    return languageSwitcher.NOT_CONTINUATION
            else:
                if(BracketStack[-1] in "}])"):
                    return languageSwitcher.CONTINUATION_END
                else:
                    return languageSwitcher.CONTINUATION_START


    def removeStrings(self, line):
        line = re.sub(PythonStringPattern, "", line)
        line = re.sub(PythonStringPattern2, "", line)
        return line
