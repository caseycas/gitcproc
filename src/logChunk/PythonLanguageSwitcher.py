import re
import BracketLanguageSwitcher

#How to combine these?
PythonFunctionPatterns = [" def +[A-Za-z_]+[\w]*\(.*\): *$", "^def +[A-Za-z_]+[\w]*\(.*\): *$"]

PythonBlockComments = ["\"\"\"", "\"\"\""] #Problem, Can be ''' or """
PythonBlockComments2 = ["\'\'\'", "\'\'\'"]
PythonSingleComment = ["#"]

PythonCommentPatterns = ["\"\"\".*\"\"\"", "\'\'\'.*\'\'\'"]
PythonCommentPattern2 = "#.*"

PythonStringPattern = "\".*?\""
PythonStringPattern2 = "\'.*?\'"

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



class PythonLanguageSwitcher():
    #Do not call this constructor outside of the Factory
    def __init__(self):
        self.lang = "Python"

    def isObjectOrientedLanguage(self):
        return True

    def getFunctionRegexes(self):
        return PythonFunctionPatterns
        
    def cleanFunctionLine(self, line):
        temp = line.strip().replace("\n", "")
        temp = temp.replace("\t", "")
        temp = temp.replace("\r", "")
   
        return temp

    def cleanClassLine(self, line):
        return line.strip().lower().replace("\n", "")

    def getClassRegexes(self):
        return PythonClassPatterns

    def isValidClassName(self, classContext):
        return re.search(PythonValidClassNamePattern, classContext)

    def cleanConstructorLine(self, line):
        return temp

    def shortenConstructorOrDestructor(self, toShorten):
        return toShorten

    def getConstructorOrDestructorRegex(self, classContext):
        #In python these are __init__ and __del__ they don't really need to be
        #treated as special cases, (so they won't fall through to here), but we should
        #have the ability to handle them if they fall through.
        return PythonConstDestrRegex + PythonParamPattern

    def parseFunctionName(self, fullName):
        #def name(): #I think it should be fine to return what falls in between the def and the first "("
        increaseIndicies = [next.start() for next in re.finditer('\(', name)]
        defLoc = fullName.find("def")
        if(defLoc == -1):
            raise ValueError("1. Function Name to parse is malformed.", fullName)
        if(len(increaseIndicies) == 0):
            raise ValueError("2. Function Name to parse is malformed.", fullName)
        if(defLoc >= increaseIndicies[0]):
            raise ValueError("3. Function Name to parse is malformed.", fullName)

        return fullName[:increaseIndicies[0]].split(" ")[-1]

    def getBlockCommentStart(self):
        start = line.find(PythonBlockComments[0])
        if(start == -1):
            start = line.find(PythonBlockComments2[0])

        return start

    def getBlockCommentEnd(self):
        end = line.find(PythonBlockComments[1])
        if(end == -1):
            end = line.find(PythonBlockComments2[1])

        return end

    def isBlockCommentStart(self):
        return(line.find(PythonBlockComments[0]) != -1 or line.find(PythonBlockComments2[0]) != -1)

    def isBlockCommentEnd(self):
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
        return line.strip().endswith(":")

    def removeStrings(self, line):
        line = re.sub(PythonStringPattern, "", line)
        line = re.sub(PythonStringPattern2, "", line)
        return line
