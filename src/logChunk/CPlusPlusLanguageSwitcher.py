import re
import BracketLanguageSwitcher

CPlusPlusFunctionPatterns = [" [\w<>\d:_]+ *[\*&]* +[\w\d_#:~|=&]+ *\([\w\d_\-=,\[\]\*\(\)&:<> ]*\) *{$",
                             " [\w<>\d:_]+ +[\*&]* *[\w\d_#:~|=&]+ *\([\w\d_\-=,\[\]\*\(\)&:<> ]*\) *{$",
                             " [\w<>\d:_]+ *[\*&]* *[\w\d_#:~|=&]+ *\([\w\d_\-=,\[\]\*\(\)&:<> ]*\) const *{$",
                             "^[\w<>\d:_]+ *[\*&]* +[\w\d_#:~|=&]+ *\([\w\d_\-=,\[\]\*\(\)&:<> ]*\) *{$",
                             "^[\w<>\d:_]+ +[\*&]* *[\w\d_#:~|=&]+ *\([\w\d_\-=,\[\]\*\(\)&:<> ]*\) *{$",
                             "^[\w<>\d:_]+ *[\*&]* *[\w\d_#:~|=&]+ *\([\w\d_\-=,\[\]\*\(\)&:<> ]*\) const *{$",
                             "template *< *class +.*> +[\w\d_#]+ *[\*&]* +[\w\d_<>:~|=&]+ *\([\w\d_\-=,\[\]\*\(\)&:<> ]*\) *{$",
                             "template *< *class +.*> +[\w\d_#]+ +[\*&]* *[\w\d_<>:~|=&]+ *\([\w\d_\-=,\[\]\*\(\)&:<> ]*\) *{$",
                             "template *< *typename +.*> +[\w\d_#]+ *[\*&]* +[\w\d_<>:~|=&]+ *\([\w\d_\-=,\[\]\*\(\)&:<> ]*\) *{$",
                             "template *< *typename +.*> +[\w\d_#]+ +[\*&]* *[\w\d_<>:~|=&]+ *\([\w\d_\-=,\[\]\*\(\)&:<> ]*\) *{$",
                             "template *< *DataType +.*> +[\w\d_#]+ *[\*&]* +[\w\d_<>:~|=&]+ *\([\w\d_\-=,\[\]\*\(\)&:<> ]*\) *{$",
                             "template *< *DataType +.*> +[\w\d_#]+ +[\*&]* *[\w\d_<>:~|=&]+ *\([\w\d_\-=,\[\]\*\(\)&:<> ]*\) *{$"]

CPlusPlusConstructorInheritsPattern = "\) *: *.*{" #Constructors only for c++

CPlusPlusBlockComments = ["/*", "*/"]
CPlusPlusSingleComment = ["//"]
CPlusPlusCommentPattern = "/\*.*?\*/"
CPlusPlusCommentPattern2 = "//.*"

#C++
CPlusPlusClassPatterns = [" class [\w\d_: ]+ {$","^class [\w\d_: ]+ {$"]
CPlusPlusStructPatterns = [" struct [\w\d_: ]+ {$","^struct [\w\d_: ]+ {$"]
CPlusPlusParamPattern = " *\([\w\d_=,\[\]\*\(\)&:<> ]*\)[^;]*{" #What parameters to a call look like.

CPlusPlusStringPattern = "\".*?\""
CPlusPlusStringPattern2 = "\'.*?\'"

CPlusPlusValidClassNamePattern = "[\w\d_:]+" 

CPlusPlusThrowPattern = "throw *\([\w\d_#:~*&]+\)"


class CPlusPlusLanguageSwitcher(BracketLanguageSwitcher.BracketLanguageSwitcher):
    #Do not call this constructor outside of the Factory
    def __init__(self, ext):
        super(CPlusPlusLanguageSwitcher, self).__init__(ext)
        self.lang = "C++"


    def isObjectOrientedLanguage(self):
        return True

    def getFunctionRegexes(self):
        return CPlusPlusFunctionPatterns
        
    def cleanFunctionLine(self, line):
        temp = line.strip().replace("\n", "")
        temp = temp.replace("\t", "")
        temp = temp.replace("\r", "")
        #Replace new lines and tabs
        #There is a weird case in hiphop-php where they included a arg1, arg2, "..."
        #Therefore, to handle this specific pseudo code case, I'm adding a special line to remove "..."
        temp = temp.replace("...", "")
        #Also, I will remove any instances of "const to deal with some tricky cases"
        temp = temp.replace(" const ", " ")
        #And weird templates with no types
        temp = temp.replace("template<>", "")
        # Get rid of " : " case that caused problems in hiphop
        temp = temp.replace(" : ", "")
        # Get rid of visibility modifiers
        temp = temp.replace("public:", "")
        temp = temp.replace("private:", "")
        temp = temp.replace("protected:", "")
        temp = temp.replace("explicit", "")
        temp = temp.replace("OVERRIDE", "")
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
        temp = temp.replace("static", "") #Quick fix.
        temp = re.sub(CPlusPlusThrowPattern,"", temp)

        return temp

    def cleanClassLine(self, line):
        return line.strip().lower().replace("\n", "")

    def isValidClassName(self, classContext):
        return re.search(CPlusPlusValidClassNamePattern, classContext)

    def getClassRegexes(self):
        return CPlusPlusClassPatterns + CPlusPlusStructPatterns #Structs can have constructors in C++ too.

    def cleanConstructorOrDestructorLine(self, line):
        temp = line.lower().strip().replace("~", "") #Just remove the "~" for destructors
        temp = temp.replace("explicit", "")
        temp = temp.replace("public:", "")
        temp = temp.replace("private:", "")
        temp = temp.replace("protected:", "")
        temp = temp.replace("\t", "")
        temp = temp.replace("\r", "")
        temp = temp.replace("\n", "")
        temp = re.sub(CPlusPlusConstructorInheritsPattern, ") {", temp)
        return temp

    def shortenConstructorOrDestructor(self, toShorten):
        return re.sub(CPlusPlusConstructorInheritsPattern, ")", toShorten)

    def getConstructorOrDestructorRegex(self, classContext):
        return classContext + CPlusPlusParamPattern

    def getBlockCommentStart(self, line):
        return line.find(CPlusPlusBlockComments[0])

    def getBlockCommentEnd(self, line):
        return line.find(CPlusPlusBlockComments[1])

    def beforeBlockCommentStart(self, line):
        start = line.find(CPlusPlusBlockComments[0])

        if(start == -1):
            return line
        else:
            return line[:start]
   
    def afterBlockCommentEnd(self, line):
        end = line.find(CPlusPlusBlockComments[1])

        if(end == -1):
            return line
        else:
            return line[end + len(CPlusPlusBlockComments[1]):]

    def getSingleComment(self):
        return CPlusPlusSingleComments

    def cleanSingleLineBlockComment(self, line):
        return re.sub(CPlusPlusCommentPattern, "", line)

    def cleanSingleLineComment(self, line):
        return re.sub(CPlusPlusCommentPattern2, "", line)

    def checkForFunctionReset(self, line):
        return line.strip().endswith(";")

    def removeStrings(self, line):
        line = re.sub(CPlusPlusStringPattern, "", line)
        line = re.sub(CPlusPlusStringPattern2, "", line)
        return line