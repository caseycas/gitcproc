#A function that returns the correct set of language regex expressions for functions
#and function like objects.
class languageSwitcher:
    extMap = {}

    def __init__(self):
        self.lang = ""

    def getLanguage(self):
        return self.lang

    #--- -> boolean 
    #Returns true if this is a recognized language that has classes, 
    #and false if it is a recognized language that doesn't contain classes.
    def isObjectOrientedLanguage(self):
        raise NotImplementedError("Base LangSwitcher is Abstract.")

    #Grab regexes associated with function expressions in our language
    def getFunctionRegexes(self):
        raise NotImplementedError("Base LangSwitcher is Abstract.")

    #For preprocessing lines that might be functions
    def cleanFunctionLine(self, line):
        raise NotImplementedError("Base LangSwitcher is Abstract.")

    #Given a well formed line matched against one of our language's
    #regular expression, retrieve the function name.
    def parseFunctionName(self, line):
        raise NotImplementedError("Base LangSwitcher is Abstract.")

    #For preprocessing lines that might be classes
    def cleanClassLine(self, line):
        raise NotImplementedError("Base LangSwitcher is Abstract.")

    #Is this name a valid class name by the rules for our language?
    def isValidClassName(self, classContext):
        raise NotImplementedError("Base LangSwitcher is Abstract.")

    #Get regexes associated with class declarations in our language
    def getClassRegexes(self):
        raise NotImplementedError("Base LangSwitcher is Abstract.")

    #For preprocessing lines that might be constructors or Destructors
    def cleanConstructorOrDestructorLine(self, line):
        raise NotImplementedError("Base LangSwitcher is Abstract.")
        
    #Additional cleaning for constructors + destructors
    def shortenConstructorOrDestructor(self, toShorten):
        raise NotImplementedError("Base LangSwitcher is Abstract.")
      
    #Get Constructor/Destructor regex
    def getConstructorOrDestructorRegex(self, classContext):
        raise NotImplementedError("Base LangSwitcher is Abstract.")

    #Get the index for the start of a block comment
    def getBlockCommentStart(self, line):
        raise NotImplementedError("Base LangSwitcher is Abstract.")

    #Get the index for the end of a block comment
    def getBlockCommentEnd(self, line):
        raise NotImplementedError("Base LangSwitcher is Abstract.")

    def isBlockCommentStart(self, line):
        raise NotImplementedError("Base LangSwitcher is Abstract.")

    def isBlockCommentEnd(self, line):
        raise NotImplementedError("Base LangSwitcher is Abstract.")

    def beforeBlockCommentStart(self, line):
        raise NotImplementedError("Base LangSwitcher is Abstract.")
   
    def afterBlockCommentEnd(self, line):
        raise NotImplementedError("Base LangSwitcher is Abstract.") 

    #Get the indicator for the start of a single line comment
    def getSingleComment(self):
        raise NotImplementedError("Base LangSwitcher is Abstract.")

    #Clean a line of all single line comments with start + end designation
    def cleanSingleLineBlockComment(self, line):
        raise NotImplementedError("Base LangSwitcher is Abstract.")

    #Clean a line of all single line comments
    def cleanSingleLineComment(self, line):
        raise NotImplementedError("Base LangSwitcher is Abstract.")

    #Have we hit something that should never be in the function pattern? (maybe a ';'')
    def checkForFunctionReset(self, line):
        raise NotImplementedError("Base LangSwitcher is Abstract.")

    #Remove all strings from a line
    def removeStrings(self, line):
        raise NotImplementedError("Base LangSwitcher is Abstract.")