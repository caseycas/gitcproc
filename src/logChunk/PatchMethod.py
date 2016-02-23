
def toStr(text):
    try:
        text1 = str(text).encode('iso-8859-1')
        temp_text = text1.replace("\'","\"")
        temp_text = temp_text.strip()
        return "\'" + str(temp_text) + "\'"
    except:
        print type(text)
        return "\'NA\'"


class PatchMethod:

    def __init__(self, name, start=0, end=0, added=0, deleted=0,keyDict={},eadd=0,edel=0,catchLineNumber=[]):
        self.method = name
        self.start = start
        self.end = end
        self.total_add = added
        self.total_del = deleted
        self.keywordDictionary= keyDict.copy()
        self.etotal_add=eadd
        self.etotal_del=edel
        self.catchLineNumber=catchLineNumber[:]

    def printPatch(self):
        #retStr  = "\n\t\t------ Method -----\n"
        retStr  = ""
        retStr += "\t\tmethod      = %s\n" % (self.method)
        retStr += "\t\tstart      = %s\n" % (self.start)
        retStr += "\t\tend      = %s\n" % (self.end)

        retStr += "\t\ttotal_add   = %d\n" % (self.total_add)
        retStr += "\t\ttotal_del   = %d\n" % (self.total_del)
        retStr += "\t\tkeywordDictonary   = %s\n" % (self.keywordDictionary)
        retStr += "\t\texception_add   = %s\n" % (self.etotal_add)
        retStr += "\t\texception_del   = %s\n" % (self.etotal_del)
        retStr += "\t\tcatchLineNumber   = %s\n" % (self.catchLineNumber)

        return retStr

    def dumpMethod(self):
        dictStr= toStr(self.method)
        for key, value in self.keywordDictionary.iteritems():
            dictStr= dictStr+","+ toStr(value)

        dictStr += "," + toStr(self.total_add) + "," + toStr(self.total_del)
    
        return dictStr

    #Get the Header string for inserting into a database.
    def getTitleString(self):
        dictStr= "(project, sha, language, file_name, is_test, method_name"
        for key, value in self.keywordDictionary.iteritems():
            dictStr= dictStr+","+ str(key).replace(" ", "_").lower() #ToStr will add ' around the strings...

        dictStr += ",total_adds,total_dels)"
    
        return dictStr

    def dictToCsv(self):
        dictStr=""
        for key, value in self.keywordDictionary.iteritems():
            if dictStr=="":
                dictStr= dictStr+toStr(value)
            else:
                dictStr= dictStr+","+ toStr(value)
            # if dictStr=="":
            #   dictStr= dictStr+(",").join((str(value)))
            # else:
            #   dictStr= dictStr+","+(",").join((str(value)))

        return str(dictStr)


    def methodToCsv(self):
        method      = toStr(self.method).replace(","," ")
        total_add   = toStr(self.total_add)
        total_del   = toStr(self.total_del)
        # unique_exception_add=toStr(self.etotal_add)
        # unique_exception_del=toStr(self.etotal_del)
        methodStr = (",").join((method,total_add,total_del,self.dictToCsv()))
        return methodStr


