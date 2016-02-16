from UnsupportedLanguageException import *

#Constants for the keywords
SINGLE = "single"
BLOCK = "block"
INCLUDED = "included"
EXCLUDED = "excluded"

KEYLISTSIZE = 3

#Constants for which phase we are in
LOOKFORNAME = 1
LOOKFOREND = 2
LOOKFOREXCP = 3
LOOKFOREXCPEND = 4

#LineTypes
ADD = 1
REMOVE = 2
OTHER = 3

#Scope Change directions
INCREASE = 1
DECREASE = 2

#Comment Change Markers
UNMARKED = 0
UNCHANGED = 1
COMADD = 2
COMDEL = 3
TOTALADD = 4
TOTALDEL = 5

#TODO: have the patterns chosen vetted by the language being parsed...

#C++
classPattern1 = " class [\w\d_: ]+ {$"
classPattern2 = "^class [\w\d_: ]+ {$"

#Needs to get Java

#notClassPattern = "class.*;.*{"
validClassNamePattern = "[\w\d_:]+"

stringPattern = "\".*?\""
stringPattern2 = "\'.*?\'"

commentPattern = "/\*.*?\*/"
commentPattern2 = "//.*"
parenPattern = "\(.*?\)"
assignPattern = "= *{"
paramPattern = " *\([\w\d_=,\[\]\*\(\)&:<> ]*\)[^;]*{" #What parameters to a call look like.

#Regex expressions for Java/C/C++ functions
#Not currently supporting things like -> in these expressions (need - as character) (Allowed in both C and C++)
#Default arguments allowed in C++, but not in C
functionPattern1 = " [\w<>\d:_]+&* *\** +[\w\d_#:~]+&* *\([\w\d_=,\[\]\*\(\)&:<> ]*\) *{$"
functionPattern2 = " [\w<>\d:_]+&* +\** *[\w\d_#:~]+&* *\([\w\d_=,\[\]\*\(\)&:<> ]*\) *{$"
functionPattern3 = " [\w<>\d:_]+&* *\** *[\w\d_#:~]+&* *\([\w\d_=,\[\]\*\(\)&:<> ]*\) const *{$" #C++ only
functionPattern4 = "^[\w<>\d:_]+&* *\** +[\w\d_#:~]+&* *\([\w\d_=,\[\]\*\(\)&:<> ]*\) *{$"
functionPattern5 = "^[\w<>\d:_]+&* +\** *[\w\d_#:~]+&* *\([\w\d_=,\[\]\*\(\)&:<> ]*\) *{$"
functionPattern6 = "^[\w<>\d:_]+&* *\** *[\w\d_#:~]+&* *\([\w\d_=,\[\]\*\(\)&:<> ]*\) const *{$" #C++ Only
functionPattern7="[\w<>\d:_]+&* *\** *[\w\d_#:~]+&* *\([\w\d_=,\[\]\*\(\)&:<> ]*\)[\s]* throws [\w\W\s]+ *{$" #Java
functionPattern8 = "^[\w<>\d:_]+&* *\** *[\w\d_#:~]+&* *\([\w\d_=,\[\]\*\(\)&:<> ]*\)[\s]* throws [\w\W\s]+ *{$" #Java
#C++ needs to have a similar one with "throw(<type>) { " instead

anonymousClassPattern= "[\s\w\d_:~]+&* * = new [\w\d_:~]+&* *\([\w\d_=,\[\]\*\(\)&:<> ]*\) *{$"
namespacePattern = "namespace.*{" #namespaces can be not named.
externPattern = "extern *{"

#Regex expressions for C++ template functions
#Add const in...
templatePattern1 = "template +< *class +.*> +[\w\d_#]+ *\** +[\w\d_<>:~]+ *\([\w\d_=,\[\]\*\(\)&:<> ]*\) *{$"
templatePattern2 = "template +< *class +.*> +[\w\d_#]+ +\** *[\w\d_<>:~]+ *\([\w\d_=,\[\]\*\(\)&:<> ]*\) *{$"
templatePattern3 = "template +< *typename +.*> +[\w\d_#]+ *\** +[\w\d_<>:~]+ *\([\w\d_=,\[\]\*\(\)&:<> ]*\) *{$"
templatePattern4 = "template +< *typename +.*> +[\w\d_#]+ +\** *[\w\d_<>:~]+ *\([\w\d_=,\[\]\*\(\)&:<> ]*\) *{$"
templatePattern5 = "template +< *DataType +.*> +[\w\d_#]+ *\** +[\w\d_<>:~]+ *\([\w\d_=,\[\]\*\(\)&:<> ]*\) *{$"
templatePattern6 = "template +< *DataType +.*> +[\w\d_#]+ +\** *[\w\d_<>:~]+ *\([\w\d_=,\[\]\*\(\)&:<> ]*\) *{$"

catchModifyPattern="- *} *catch.*{\s*\+ *} *catch.*{\s*"

constructorInheritsPattern = "\) *: *.*{" #Constructors only for c++

#Label for structures found outside of a function
MOCK = "NO_FUNC_CONTEXT"

#A function that returns the correct set of language regex expressions for functions
#and function like objects.
class languageSwitcher:
	def __init__(self, language):
		#TODO: Apply switcher that maps extension to language
		self.lang = language

	#def getFunctionPatterns(self):
	#	if(self.lang == "C"):
    #
	#	elif(self.lang == "C++"):
	#	elif(self.lang == "Java"):
	#	elif(self.lang == "Python"):
	#    else:
	#    	except UnsupportedLanguageException("Function patterns in " + self.lang + " not yet supported.")

    #Get OO related patterns if applicable
	#def getClassPatterns(self):

	#Get other patterns with scope Change
	#def getOtherPatterns(self):