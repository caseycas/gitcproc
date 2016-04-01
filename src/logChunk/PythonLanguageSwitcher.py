import re
import BracketLanguageSwitcher

#How to combine these?
PythonFunctionPatterns = [" def +\(.*\): *$", "^def +\(.*\): *$"]

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
        raise NotImplementedError("Not implemented yet for python.")

    def isValidClassName(self, name):
        raise NotImplementedError("Not implemented yet for python.")

    def cleanConstructorLine(self, line):
        return temp

    def shortenConstructorOrDestructor(self, toShorten):
        return toShorten

    def getConstructorOrDestructorRegex(self, classContext):
        raise NotImplementedError("Not implemented yet for python.")

    def parseFunctionName(self, fullName):
        raise NotImplementedError("Not implemented yet for python.")

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
