__author__ = 'yagniks'


import codecs
import re

ADD = 1
REMOVE = 2
OTHER = 3
LOOKFORNAME=1
LOOKFOREND=2
classPattern1 = " class [\w\d_: ]+ {$"
classPattern2 = "^class [\w\d_: ]+ {$"

#notClassPattern = "class.*;.*{"
validClassNamePattern = "[\w\d_:]+"

stringPattern = "\".*\""
commentPattern = "/\*.*\*/"
commentPattern2 = "//.*"
parenPattern = "\(.*\)"
assignPattern = "= *{"
paramPattern = " *\([\w\d_,\[\]\*\(\)&: ]*\)[^;]*{" #What parameters to a call look like.
functionPattern1 = " [\w\d:_]+&* *\** +[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
functionPattern2 = " [\w\d:_]+&* +\** *[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
functionPattern3 = " [\w\d:_]+&* *\** *[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) const *{$"
functionPattern4 = " [\w\d:_]+&* *\** *[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) throws \w+ *{$"
functionPattern5 = "^[\w\d:_]+&* *\** +[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
functionPattern6 = "^[\w\d:_]+&* +\** *[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
functionPattern7 = "^[\w\d:_]+&* *\** *[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) const *{$"
functionPattern8 = "^[\w\d:_]+&* *\** *[\w\d_:~]+&* *\([\w\d_,\[\]\*\(\)&:<> ]*\) throws \w+ *{$"

namespacePattern = "namespace.*{" #namespaces can be not named.
externPattern = "extern *{"

templatePattern1 = "template +< *class +.*> +[\w\d_]+ *\** +[\w\d_<>:~]+ *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
templatePattern2 = "template +< *class +.*> +[\w\d_]+ +\** *[\w\d_<>:~]+ *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
templatePattern3 = "template +< *typename +.*> +[\w\d_]+ *\** +[\w\d_<>:~]+ *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
templatePattern4 = "template +< *typename +.*> +[\w\d_]+ +\** *[\w\d_<>:~]+ *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
templatePattern5 = "template +< *DataType +.*> +[\w\d_]+ *\** +[\w\d_<>:~]+ *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"
templatePattern6 = "template +< *DataType +.*> +[\w\d_]+ +\** *[\w\d_<>:~]+ *\([\w\d_,\[\]\*\(\)&:<> ]*\) *{$"

functions=[]

class functionObj:

    def __init__(self, name, start=0, end=0, added=0, deleted=0):
        self.name = name.strip()
        self.start = start
        self.end = end
        self.assertionList = [] #List of triples - line #, line type, actual assert
        self.total_add = added
        self.total_del = deleted



def getFunctionPattern(line):
    #Replace new lines and tabs
    temp = line.strip().replace("\n", "")
    temp = temp.replace("\t", "")
    temp = temp.replace("\r", "")
    #There is a weird case in hiphop-php where they included a arg1, arg2, "..."
    #Therefore, to handle this specific pseudo code case, I'm adding a special line to remove "..."
    temp = temp.replace("...", "")
    #Also, I will remove any instances of "const to deal with some tricky cases"
    temp = temp.replace(" const ", "")
    #And weird templates with no types
    temp = temp.replace("template<>", "")
    # Get rid of " : " case that caused problems in hiphop
    temp = temp.replace(" : ", "")
    # Get rid of visibility modifiers
    temp = temp.replace("public:", "")
    temp = temp.replace("private:", "")
    temp = temp.replace("protected:", "")
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
    temp = temp.replace("else", "")
    temp = temp.replace("if", "")



    #Check for regular and template functions
    if("template" in temp):
        temp = temp.replace("static", "") #Quick fix.

        result = re.search(templatePattern1, temp)
        if(result != None):
            return result.group(0)
        result = re.search(templatePattern2, temp)
        if(result != None):
            return result.group(0)
        result = re.search(templatePattern3, temp)
        if(result != None):
            return result.group(0)
        result = re.search(templatePattern4, temp)
        if(result != None):
            return result.group(0)
        result = re.search(templatePattern5, temp)
        if(result != None):
            return result.group(0)
        result = re.search(templatePattern6, temp)
        if(result != None):
            return result.group(0)

        return ""

    else:
        result = re.search(functionPattern1, temp)
        if(result != None):
            return result.group(0)
        result = re.search(functionPattern2, temp)
        if(result != None):
            return result.group(0)
        result = re.search(functionPattern3, temp)
        if(result != None):
            return result.group(0)
        result = re.search(functionPattern4, temp)
        if(result != None):
            return result.group(0)
        result = re.search(functionPattern5, temp)
        if(result != None):
            return result.group(0)
        result = re.search(functionPattern6, temp)
        if(result != None):
            return result.group(0)
        result = re.search(functionPattern7, temp)
        if(result != None):
            return result.group(0)
        result = re.search(functionPattern8, temp)
        if(result != None):
            return result.group(0)


        return ""


inf = codecs.open("test1.txt", "r", "iso-8859-1")
lineNum=0
total_add=0
total_del=0
chunk=""

bracketDepth = 0
lineType = OTHER
phase = LOOKFORNAME
commentFlag = False #Are we inside a comment?
functionName = ""
shortFunctionName = ""
funcStart = 0
funcEnd = 0
nestingDepth = 0 # How many brackets should be open to say this function is closed?
ctotal_add = 0 # How many lines added in this function
ctotal_del = 0 # How many lines deleted in this function
classContext = [] #If we are parsing inside a class, what is the closest class name?
total_add=0



#Asserts outside of function (1 per chunk)
exceptionNoFunc = []
#Asserts inside the current function
exceptionCurFunc = []
isFunction=False

for line in inf:
     lineNum += 1
     fullLine = line.strip()
     line = fullLine
     if not line.strip():
         continue
     if(line.startswith("+")):
         lineType = ADD
         line = line[1:]
         ctotal_add+=1
         if(phase == LOOKFOREND):
             total_add += 1
     if(line.startswith("-")):
         lineType = REMOVE
         line = line[1:]
         ctotal_del+=1
         if(phase == LOOKFOREND):
             total_del += 1


 #Remove all strings from the line. (Get rid of wierd cases of brackets
    #or comment values being excluded from the line.
     line = re.sub(stringPattern, "", line)

    #If there is a comment of the form /* .... */ (single line only) remove it.
     line = re.sub(commentPattern, "", line)

    #Remove // comments from the string
     line = re.sub(commentPattern2, "", line)

    #print("Next Line: " + line)

    #Ignore multiple line comments
     if(line.find("/*") != -1):
         commentFlag = True
        #We need to consider the content of the line before the /*
         line = line.split("/*")[0]
     elif(line.find("*/") != -1):
         if(commentFlag):
             commentFlag = False
         elif(phase == LOOKFORNAME): #Case where only bottom part of comment is changed and looking for function name.
             functionName = "" #Clear the function name

         index = line.find("*/")
         if(len(line) > index + 2):
             line = line[index + 2:]
         else:
             continue
     elif(commentFlag):
         continue



     if(phase == LOOKFORNAME):
         bracketDepth += line.count("{")
         if(line.strip().endswith(";")):
             functionName = "" #Clear the name



         if(bracketDepth > nestingDepth):

            if("{" in line):
                functionName += line.split("{")[0] + "{"
            else:
                functionName += line.split("{")[0]

            shortFunctionName = getFunctionPattern(functionName)
            if(shortFunctionName != ""):
                isFunction=True
            else:
                isFunction=False

            if(isFunction): #Skip things are aren't functions
                funcStart = lineNum
                phase = LOOKFOREND
                if(lineType == REMOVE):
                    total_del = 1
                elif(lineType == ADD):
                    total_add = 1

            else:
                nestingDepth +=1

                functionName=""


         else: #No brackets to cut off, so add the whole line instead
                        functionName += line.replace("\n", "") + " " #add the line with no new lines

         bracketDepth -= line.count("}")
         print bracketDepth,nestingDepth,phase
         if(bracketDepth == nestingDepth and phase == LOOKFOREND):
             funcEnd = lineNum
             funcToAdd = functionObj(shortFunctionName, funcStart, funcEnd, total_add, total_del)
             functions.append(funcToAdd)







     functionName = ""
     shortFunctionName = ""
     funcStart = 0
     funcEnd = 0
     total_add = 0
     total_del = 0
     phase = LOOKFORNAME



#     if re.search("try *{",line,re.DOTALL | re.MULTILINE):






print "ctotal add", ctotal_add
print "ctotal del", ctotal_del



