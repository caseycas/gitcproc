import re
import BracketLanguageSwitcher

#How to combine these?
CFunctionPatterns = [" [\w<>\d:_]+ *[\*&]* +[\w\d_#:~]+&* *\([\w\d_\-,\[\]\*\(\)&:<> ]*\) *{$",
             " [\w<>\d:_]+ +[\*&]* *[\w\d_#:~]+&* *\([\w\d_\-,\[\]\*\(\)&:<> ]*\) *{$",
             "^[\w<>\d:_]+ *[\*&]* +[\w\d_#:~]+&* *\([\w\d_\-,\[\]\*\(\)&:<> ]*\) *{$",
             "^[\w<>\d:_]+ +[\*&]* *[\w\d_#:~]+&* *\([\w\d_\-,\[\]\*\(\)&:<> ]*\) *{$"]

CBlockComments = ["/*", "*/"]
CSingleComment = ["//"]

CCommentPattern = "/\*.*?\*/"
CCommentPattern2 = "//.*"

CStringPattern = "\".*?\""
CStringPattern2 = "\'.*?\'"



class CLanguageSwitcher(BracketLanguageSwitcher.BracketLanguageSwitcher):
    #Do not call this constructor outside of the Factory
    def __init__(self, ext):
        super(CLanguageSwitcher, self).__init__(ext)
        self.lang = "C"


    def isObjectOrientedLanguage(self):
        return False

    def getFunctionRegexes(self):
        return CFunctionPatterns
        
    def cleanFunctionLine(self, line):
        temp = line.strip().replace("\n", "")
        temp = temp.replace("\t", "")
        temp = temp.replace("\r", "")
        #Sometimes an # ifdef, etc might appear in the middle of function args.  Purge them!
        if("ifdef" in temp and "#" in temp):
            temp = temp.replace("#", "")
            temp = temp.replace("ifdef", "")
        if("endif" in temp and "#" in temp):
            temp = temp.replace("#", "")
            temp = temp.replace("endif", "")
        if("ifndef" in temp and "#" in temp):
            temp = temp.replace("#", "")
            temp = temp.replace("ifndef", "")
        #Deal with if statements...
        temp = re.sub(" else", "", temp)
        temp = re.sub("^else", "", temp)
        temp = re.sub(" if", "", temp)
        temp = re.sub("^if", "", temp)
        temp = re.sub(" +\d+ +", "", temp) #Replace numbers

        return temp

    def cleanClassLine(self, line):
        raise NotImplementedError("C doesn't have classes.")

    def getClassRegexes(self):
        raise NotImplementedError("C doesn't have classes.")

    def isValidClassName(self, name):
        raise NotImplementedError("C doesn't have classes.")

    def cleanConstructorLine(self, line):
        raise NotImplementedError("C doesn't have classes.")

    def shortenConstructorOrDestructor(self, toShorten):
        raise NotImplementedError("C doesn't have classes.")

    def getConstructorOrDestructorRegex(self, classContext):
        raise NotImplementedError("C doesn't have classes.")

    def getBlockCommentStart(self, line):
        return line.find(CBlockComments[0])

    def getBlockCommentEnd(self, line):
        return line.find(CBlockComments[1])

    def beforeBlockCommentStart(self, line):
        start = line.find(CBlockComments[0])

        if(start == -1):
            return line
        else:
            return line[:start]
   
    def afterBlockCommentEnd(self, line):
        end = line.find(CBlockComments[1])

        if(end == -1):
            return line
        else:
            return line[end + len(CBlockComments[1]):]

    def getSingleComment(self):
        return CSingleComments

    def cleanSingleLineBlockComment(self, line):
        return re.sub(CCommentPattern, "", line)

    def cleanSingleLineComment(self, line):
        return re.sub(CCommentPattern2, "", line)

    def checkForFunctionReset(self, line):
        return line.strip().endswith(";")

    def removeStrings(self, line):
        line = re.sub(CStringPattern, "", line)
        line = re.sub(CStringPattern2, "", line)
        return line
