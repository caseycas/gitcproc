import unittest
import logChunk
from chunkingConstants import *

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


        self.testChunk = logChunk.logChunk("", "Python")

        self.chunk1 = logChunk.logChunk(self.readHelper("testfiles/Python/testChunk1.txt"), "Python", "../util/sample_confPy.ini")


    #def test_FunctionNameParse(self):

    #def test_isClassDef(self):


    #def test_isConstructorOrDestructor(self):


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


    def test_parseText1(self):
        self.chunk1.parseText()
        funcList = self.chunk1.functions
        self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 1) 
        self.assertTrue(funcList[0].method=="_ask_default")
        self.assertTrue(funcList[0].total_add == 1)
        self.assertTrue(funcList[0].total_del == 1)

        testDict = {'print Adds': 1, 'print Dels': 1, 'if Dels': 0, 'if Adds': 0}

        self.assertEqual(testDict,funcList[0].keywordDictionary)



if __name__=="__main__":
    unittest.main()
