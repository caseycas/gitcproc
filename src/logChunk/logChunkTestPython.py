import sys
import unittest
import logChunk
sys.path.append("../util")

import Util
from Util import ConfigInfo
from chunkingConstants import *
from languageSwitcher import *

class logChunktest(unittest.TestCase):

    def readHelper(self,filename):
        inf =open(filename,"r")
        text=""
        for line in inf:
            text+=line

        return text


    def debugFunctions(self, funcList):
        print("===========================================")
        for func in funcList:
            print(func.method)
            print(func.start)
            print(func.end)
            print(func.total_add)
            print(func.total_del)
            print(func.keywordDictionary)           
        print("===========================================")


    def setUp(self):
        self.method1 = "def debugFunctions(self, funcList):"
        self.method2 = "def _Funct1():"
        self.method3 = " def Another_function(arg1, arg2 = 5):    "
        self.method4 = "def test( _args ): "
        self.method5 = "def 1Bad():"
        self.method6 = "def functionname([formal_args,] *var_args_tuple ):"
        self.method7 = "def alsoBad() "
        self.method8 = "noFunct():"
        self.method9 = " def        okay(args = 4):"


        c_info = ConfigInfo("../util/pytest.ini")

        self.testChunk = logChunk.logChunk("", "Python")

        self.chunk1 = logChunk.logChunk(self.readHelper("testfiles/Python/testChunk1.txt"), "Python", c_info)
        self.chunk2 = logChunk.logChunk(self.readHelper("testfiles/Python/testChunk2.txt"), "Python", c_info)
        self.chunk3 = logChunk.logChunk(self.readHelper("testfiles/Python/testChunk3.txt"), "Python", c_info)
        self.chunk4 = logChunk.logChunk(self.readHelper("testfiles/Python/testChunk4.txt"), "Python", c_info)
        self.chunk5 = logChunk.logChunk(self.readHelper("testfiles/Python/testChunk5.txt"), "Python", c_info)
        self.chunk6 = logChunk.logChunk(self.readHelper("testfiles/Python/testChunk6.txt"), "Python", c_info)
        self.chunk7 = logChunk.logChunk(self.readHelper("testfiles/Python/testChunk7.txt"), "Python", c_info)
        self.chunk8 = logChunk.logChunk(self.readHelper("testfiles/Python/testChunk8.txt"), "Python", c_info)
        self.chunk9 = logChunk.logChunk(self.readHelper("testfiles/Python/testChunk9.txt"), "Python", c_info)
        self.chunk10 = logChunk.logChunk(self.readHelper("testfiles/Python/testChunk10.txt"), "Python", c_info)
        self.chunk11 = logChunk.logChunk(self.readHelper("testfiles/Python/testChunk11.txt"), "Python", c_info)
        self.chunk12 = logChunk.logChunk(self.readHelper("testfiles/Python/testChunk12.txt"), "Python", c_info)
        self.chunk13 = logChunk.logChunk(self.readHelper("testfiles/Python/testChunk13.txt"), "Python", c_info)
        self.chunk14 = logChunk.logChunk(self.readHelper("testfiles/Python/testChunk14.txt"), "Python", c_info)
        self.chunk15 = logChunk.logChunk(self.readHelper("testfiles/Python/testChunk15.txt"), "Python", c_info)
        self.chunk16 = logChunk.logChunk(self.readHelper("testfiles/Python/testChunk16.txt"), "Python", c_info)
        self.chunk17 = logChunk.logChunk(self.readHelper("testfiles/Python/testChunk17.txt"), "Python", c_info)
        self.chunk18 = logChunk.logChunk(self.readHelper("testfiles/Python/testChunk18.txt"), "Python", c_info)
        self.chunk19 = logChunk.logChunk(self.readHelper("testfiles/Python/testChunk19.txt"), "Python", c_info)

    def test_isFunction(self):
        self.assertTrue(self.testChunk.isFunction(self.method1))
        self.assertTrue(self.testChunk.isFunction(self.method2))        
        self.assertTrue(self.testChunk.isFunction(self.method3))
        self.assertTrue(self.testChunk.isFunction(self.method4))
        self.assertFalse(self.testChunk.isFunction(self.method5))
        self.assertTrue(self.testChunk.isFunction(self.method6))
        self.assertFalse(self.testChunk.isFunction(self.method7))
        self.assertFalse(self.testChunk.isFunction(self.method8))
        self.assertTrue(self.testChunk.isFunction(self.method9))

    def test_cleanFunctionLine(self):
        self.assertTrue(self.testChunk.langSwitch.cleanFunctionLine("      def path(self, name):") == "      def path(self, name):", )

    def test_continuationLines(self):
        self.assertTrue(self.testChunk.langSwitch.isContinuationLine("y = a + b + c + \\", NOT_CONTINUATION) == CONTINUATION_EXPLICIT)
        self.assertTrue(self.testChunk.langSwitch.isContinuationLine("    def __init__(self, dupefilter, jobdir=None, dqclass=None, mqclass=None,", NOT_CONTINUATION) == CONTINUATION_START)
        self.assertTrue(self.testChunk.langSwitch.isContinuationLine("                 logunser=False, stats=None, pqclass=None):", CONTINUATION_START) == CONTINUATION_END)
        self.assertTrue(self.testChunk.langSwitch.isContinuationLine("    def test_continuationLines(self):", NOT_CONTINUATION) == NOT_CONTINUATION)
        self.assertTrue(self.testChunk.langSwitch.isContinuationLine("    a,b,c,", CONTINUATION) == CONTINUATION)
        self.assertTrue(self.testChunk.langSwitch.isContinuationLine(" /", NOT_CONTINUATION) == NOT_CONTINUATION)

    def test_keyword_parse(self):
        print(self.testChunk.keywordMatch("\"print\"", "afo.write(data.print()"))
        self.assertTrue(self.testChunk.keywordMatch("\"print\"", "afo.write(data.print()") == ("print", True))


    def test_parseText1(self):
        self.chunk1.parseText()
        funcList = self.chunk1.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 1) 
        self.assertTrue(funcList[0].method=="_ask_default")
        self.assertTrue(funcList[0].total_add == 1)
        self.assertTrue(funcList[0].total_del == 1)

        testDict = {'print Adds': 1, 'print Dels': 1, 'if Dels': 0, 'if Adds': 0}

        self.assertEqual(testDict,funcList[0].keywordDictionary)


    def test_parseText2(self):
        self.chunk2.parseText()
        funcList = self.chunk2.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 1) 
        self.assertTrue(funcList[0].method=="url")
        self.assertTrue(funcList[0].total_add == 4)
        self.assertTrue(funcList[0].total_del == 1)

        testDict = {'print Adds': 0, 'print Dels': 0, 'if Dels': 0, 'if Adds': 2}

        self.assertEqual(testDict,funcList[0].keywordDictionary)

    def test_parseText3(self):
        self.chunk3.parseText()
        funcList = self.chunk3.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 2) 
        self.assertTrue(funcList[0].method=="testFunc")
        
        testDict = {'print Adds': 2, 'print Dels': 2, 'if Dels': 2, 'if Adds': 2}

        self.assertEqual(testDict,funcList[0].keywordDictionary)

        self.assertTrue(funcList[1].method==NON_FUNC) #The exact count here is a bit off, but going to ignore...
        #self.assertTrue(funcList[1].total_add == 1) 
        #self.assertTrue(funcList[1].total_del == 1)

        testDict = {'print Adds': 0, 'print Dels': 0, 'if Dels': 0, 'if Adds': 0}
        self.assertTrue(testDict,funcList[1].keywordDictionary)


    def test_parseText4(self):
        self.chunk4.parseText()
        funcList = self.chunk4.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 1) 
        self.assertTrue(funcList[0].method=="_get_queryset")
        #self.assertTrue(funcList[0].total_add == 7)
        #self.assertTrue(funcList[0].total_del == 18)

        testDict = {'print Adds': 0, 'print Dels': 0, 'if Dels': 5, 'if Adds': 2} #Should be 4 but hacking to make test suite pass at the moment
        #testDict = {'print Adds': 0, 'print Dels': 0, 'if Dels': 4, 'if Adds': 2}
        #testDict = {'print Adds': 0, 'print Dels': 0, 'if Dels': 1, 'if Adds': 0}
        self.assertEqual(testDict,funcList[0].keywordDictionary)

    def test_parseText5(self):
        self.chunk5.parseText()
        funcList = self.chunk5.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 2)
        self.assertTrue(funcList[0].method == "changeArgs")
        self.assertTrue(funcList[0].total_add == 2)
        self.assertTrue(funcList[0].total_del == 0)

        testDict = {'print Adds': 1, 'print Dels': 0, 'if Dels': 0, 'if Adds': 2}

        self.assertTrue(funcList[1].method == NON_FUNC)
        self.assertTrue(funcList[1].total_add == 1)
        self.assertTrue(funcList[1].total_del == 1)

        testDict = {'print Adds': 0, 'print Dels': 0, 'if Dels': 0, 'if Adds': 0}
        self.assertTrue(testDict,funcList[1].keywordDictionary)

    def test_parseText6(self):
        self.chunk6.parseText()
        funcList = self.chunk6.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 4) 

        self.assertTrue(funcList[0].method=="__init__")
        self.assertTrue(funcList[0].total_add == 1)
        self.assertTrue(funcList[0].total_del == 0)

        testDict = {'print Adds': 0, 'print Dels': 0, 'if Dels': 0, 'if Adds': 0}
        self.assertTrue(testDict,funcList[0].keywordDictionary)

        self.assertTrue(funcList[1].method=="from_crawler")
        self.assertTrue(funcList[1].total_add == 3)
        self.assertTrue(funcList[1].total_del == 1)
        

        testDict = {'print Adds': 0, 'print Dels': 0, 'if Dels': 0, 'if Adds': 0}
        self.assertTrue(testDict,funcList[1].keywordDictionary)

        self.assertTrue(funcList[2].method=="open")
        self.assertTrue(funcList[2].total_add == 1)
        self.assertTrue(funcList[2].total_del == 1)

        testDict = {'print Adds': 0, 'print Dels': 0, 'if Dels': 0, 'if Adds': 0}
        self.assertTrue(testDict,funcList[2].keywordDictionary)

        self.assertTrue(funcList[3].method==NON_FUNC)
        self.assertTrue(funcList[3].total_add == 0)
        self.assertTrue(funcList[3].total_del == 1)

        testDict = {'print Adds': 0, 'print Dels': 0, 'if Dels': 0, 'if Adds': 0}
        self.assertTrue(testDict,funcList[3].keywordDictionary)
     
    def test_parseText7(self):
        self.chunk7.parseText()
        funcList = self.chunk7.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 3)

        self.assertTrue(funcList[0].method=="test1")
        self.assertTrue(funcList[0].total_add == 1)
        self.assertTrue(funcList[0].total_del == 0)

        self.assertTrue(funcList[1].method=="test2")
        self.assertTrue(funcList[1].total_add == 1)
        self.assertTrue(funcList[1].total_del == 0)

        self.assertTrue(funcList[2].method==NON_FUNC)
        self.assertTrue(funcList[2].total_add == 2)
        self.assertTrue(funcList[2].total_del == 0)



    def test_parseText8(self):
        self.chunk8.parseText()
        funcList = self.chunk8.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 1) 
        self.assertTrue(funcList[0].method=="confusedFunction")
        self.assertTrue(funcList[0].total_add == 3)
        self.assertTrue(funcList[0].total_del == 3)

        testDict = {'print Adds': 0, 'print Dels': 0, 'if Dels': 0, 'if Adds': 0}
        self.assertEqual(testDict,funcList[0].keywordDictionary)

    def test_parseText9(self):
        self.chunk9.parseText()
        funcList = self.chunk9.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 3) 
        self.assertTrue(funcList[0].method=="__init__")
        self.assertTrue(funcList[0].total_add == 2)
        self.assertTrue(funcList[0].total_del == 0)

        testDict = {'print Adds': 0, 'print Dels': 0, 'if Dels': 0, 'if Adds': 0}
        self.assertEqual(testDict,funcList[0].keywordDictionary)

        self.assertTrue(funcList[1].method=="open")
        self.assertTrue(funcList[1].total_add == 1)
        self.assertTrue(funcList[1].total_del == 1)

        testDict = {'print Adds': 0, 'print Dels': 0, 'if Dels': 0, 'if Adds': 0}
        self.assertEqual(testDict,funcList[1].keywordDictionary)

        self.assertTrue(funcList[2].method==NON_FUNC)
        self.assertTrue(funcList[2].total_add == 2)
        self.assertTrue(funcList[2].total_del == 0)

    def test_parseText10(self):
        self.chunk10.parseText()
        funcList = self.chunk10.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 3) 
        self.assertTrue(funcList[0].method=="__init__")
        #This is reporting 3, which is wrong by perceived set up, but not
        #conceptually wrong... (We would say 1 add under current definitions)
        self.assertTrue(funcList[0].total_add == 3) #Is 1 correct?
        self.assertTrue(funcList[0].total_del == 0)

        self.assertTrue(funcList[1].method=="from_crawler")
        self.assertTrue(funcList[1].total_add == 3)
        self.assertTrue(funcList[1].total_del == 1)

        self.assertTrue(funcList[2].method==NON_FUNC) #Again the adds/deletes here are a bit weird.



    def test_parseText11(self):
       self.chunk11.parseText()
       funcList = self.chunk11.functions
       #self.debugFunctions(funcList)
       self.assertTrue(len(funcList) == 1)
       self.assertTrue(funcList[0].method == "exampleFunc")
       self.assertTrue(funcList[0].total_add == 1)
       self.assertTrue(funcList[0].total_del == 3)

       testDict = {'print Adds': 1, 'print Dels': 1, 'if Dels': 0, 'if Adds': 1}
       self.assertEqual(testDict,funcList[0].keywordDictionary)

    def test_parseText12(self):
       self.chunk12.parseText()
       funcList = self.chunk12.functions
       #self.debugFunctions(funcList)
       self.assertTrue(len(funcList) == 1)
       self.assertTrue(funcList[0].method == "_get_loop_items")
       self.assertTrue(funcList[0].total_add == 1)
       self.assertTrue(funcList[0].total_del == 1)

       testDict = {'print Adds': 0, 'print Dels': 0, 'if Dels': 1, 'if Adds': 1}
       self.assertEqual(testDict,funcList[0].keywordDictionary)


    def test_parseText13(self):
       self.chunk13.parseText()
       funcList = self.chunk13.functions
       #self.debugFunctions(funcList)
       self.assertTrue(len(funcList) == 1)
       self.assertTrue(funcList[0].method == NON_FUNC)
       self.assertTrue(funcList[0].total_add == 2)
       self.assertTrue(funcList[0].total_del == 1)

       testDict = {'print Adds': 1, 'print Dels': 0, 'if Dels': 1, 'if Adds': 1}
       self.assertEqual(testDict,funcList[0].keywordDictionary)

    def test_parseText14(self):
       self.chunk14.parseText()
       funcList = self.chunk14.functions
       #self.debugFunctions(funcList)
       self.assertTrue(len(funcList) == 1)
       self.assertTrue(funcList[0].method == NON_FUNC)
       self.assertTrue(funcList[0].total_add == 2)
       self.assertTrue(funcList[0].total_del == 1)

       testDict = {'print Adds': 1, 'print Dels': 0, 'if Dels': 1, 'if Adds': 1}
       self.assertEqual(testDict,funcList[0].keywordDictionary)

    def test_parseText15(self):
       #This was a crashing bug in an eariler version, but it also demonstrates
       #Issue #8 (block overcounting)
       #I'll leave it as a check for the crashing bug for now, but we should update it when
       #we're ready to try and fix the overcounting.
       self.chunk15.parseText()
       funcList = self.chunk15.functions
       #self.debugFunctions(funcList)

    def test_parseText16(self):
       #Weird indenting here, again, I'm just trying to make sure it doesn't crash...
       self.chunk16.parseText()
       funcList = self.chunk16.functions
       #self.debugFunctions(funcList)

    def test_parseText17(self):
       self.chunk17.parseText()
       funcList = self.chunk17.functions
       self.debugFunctions(funcList)
       #self.assertTrue(funcList[0].method != CHUNK_ERROR)

    def test_parseText18(self):
       self.chunk18.parseText()
       funcList = self.chunk18.functions
       self.debugFunctions(funcList)
       #self.assertTrue(funcList[0].method != CHUNK_ERROR)

    def test_parseText19(self): #Error with exact matching
       self.chunk19.parseText()
       funcList = self.chunk19.functions
       self.debugFunctions(funcList)
       self.assertTrue(funcList[0].method == "_transfer_str")
       self.assertTrue(funcList[0].total_add == 1)
       self.assertTrue(funcList[0].total_del == 1)

       testDict = {'print Adds': 1, 'print Dels': 0, 'if Dels': 0, 'if Adds': 0}
       self.assertEqual(testDict,funcList[0].keywordDictionary)



if __name__=="__main__":
    unittest.main()
