import re
import BracketLanguageSwitcher

#---------------------- Yagnik double check these ----------------------
'''
JavaFunctionPatterns = [" [\w<>\d:_]+&* *\** +[\w\d_#:~]+&* *\([\w\d_=,\[\]\*\(\)&:<> ]*\) *{$",
                             " [\w<>\d:_]+&* +\** *[\w\d_#:~]+&* *\([\w\d_=,\[\]\*\(\)&:<> ]*\) *{$",
                             "^[\w<>\d:_]+&* *\** +[\w\d_#:~]+&* *\([\w\d_=,\[\]\*\(\)&:<> ]*\) *{$",
                                 "^[\w<>\d:_]+&* +\** *[\w\d_#:~]+&* *\([\w\d_=,\[\]\*\(\)&:<> ]*\) *{$",
                             "[\w<>\d:_]+&* *\** *[\w\d_#:~]+&* *\([\w\d_=,\[\]\*\(\)&:<> ]*\)[\s]* throws [\w\W\s]+ *{$",
                             "^[\w<>\d:_]+&* *\** *[\w\d_#:~]+&* *\([\w\d_=,\[\]\*\(\)&:<> ]*\)[\s]* throws [\w\W\s]+ *{$"]

'''
# JavaFunctionPatterns = ["(public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(\{?|[^;])"]

JavaFunctionPatterns=["((public|private|protected|static|final|native|synchronized|abstract|transient)+\s*)+[\$_\w\<\>\[\]]*\s+[\$_\w]+\([^\)]*\)?\s*\{?[^\}]*\}?"]

JavaParamPattern = " *\([\w\d_=,\[\]\*\(\)&:<> ]*\)[^;]*{" #What parameters to a call look like. C/C++/Java specific

JavaBlockComments = ["/*", "*/"]
JavaSingleComment = ["//"]

JavaCommentPattern = "/\*.*?\*/"
JavaCommentPattern2 = "//.*"

JavaStringPattern = "\".*?\""
JavaStringPattern2 = "\'.*?\'"

JavaClassPatterns = [" class [\w\d_: ]+ {$","^class [\w\d_: ]+ {$"] 

JavaValidClassNamePattern = "[\w\d_:]+" 

#Do we need this?
#anonymousClassPattern= "[\s\w\d_:~]+&* * = new [\w\d_:~]+&* *\([\w\d_=,\[\]\*\(\)&:<> ]*\) *{$"

#---------------------- Yagnik double check these ----------------------



class JavaLanguageSwitcher(BracketLanguageSwitcher.BracketLanguageSwitcher):
    #Do not call this constructor outside of the Factory
    def __init__(self, ext):
        super(JavaLanguageSwitcher, self).__init__(ext)
        self.lang = "Java"


    def isObjectOrientedLanguage(self):
        return True

    def getFunctionRegexes(self):
        return JavaFunctionPatterns
        
    def cleanFunctionLine(self, line):
        temp = line.strip().replace("\n", "")
        temp = temp.replace("\t", "")
        temp = temp.replace("\r", "")
        temp = re.sub(" else", "", temp)
        temp = re.sub("^else", "", temp)
        temp = re.sub(" if", "", temp)
        temp = re.sub("^if", "", temp)
        temp = temp.replace("static", "") #Quick fix.

        return temp

    def cleanClassLine(self, line):
        return line.strip().lower().replace("\n", "")

    def isValidClassName(self, classContext):
        return re.search(JavaValidClassNamePattern, classContext)

    def getClassRegexes(self):
        return JavaClassPatterns

    def cleanConstructorOrDestructorLine(self, line):
        return line

    def shortenConstructorOrDestructor(self, toShorten):
        return toShorten

    def getConstructorOrDestructorRegex(self, classContext):
        return classContext + JavaParamPattern

    def getBlockCommentStart(self, line):
        return line.find(JavaBlockComments[0])

    def getBlockCommentEnd(self, line):
        return line.find(JavaBlockComments[1])

    def beforeBlockCommentStart(self, line):
        start = line.find(JavaBlockComments[0])

        if(start == -1):
            return line
        else:
            return line[:start]
   
    def afterBlockCommentEnd(self, line):
        end = line.find(JavaBlockComments[1])

        if(end == -1):
            return line
        else:
            return line[end + len(JavaBlockComments[1]):]


    def getSingleComment(self):
        return JavaSingleComments

    def cleanSingleLineBlockComment(self, line):
        return re.sub(JavaCommentPattern, "", line)

    def cleanSingleLineComment(self, line):
        return re.sub(JavaCommentPattern2, "", line)

    def checkForFunctionReset(self, line):
        return line.strip().endswith(";")

    def removeStrings(self, line):
        line = re.sub(JavaStringPattern, "", line)
        line = re.sub(JavaStringPattern2, "", line)
        return line