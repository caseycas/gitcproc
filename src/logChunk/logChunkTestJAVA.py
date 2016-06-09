import sys
import unittest
import logChunk
from chunkingConstants import *
sys.path.append("../util")

import Util
from Util import ConfigInfo

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
        self.javaMethod1 = "public static Intent createIntent(Context context, String username, String password) {"
        self.javaMethod2 = " public <V> V post(final String uri, final Object params, final Type type) \n throws IOException {"
        self.javaMethod3 = "public static Intent createIntent(final Collection<? extends Issue> issues,\n final Repository repository, final int position) {"
        self.javaMethod4 = "@Override \n public List<User> run(Account account) throws Exception {"
        self.javaMethod5 = "private JClass typeBoundsToJClass(GeneratedClassHolder holder, List<? extends TypeMirror> bounds, Map<String, TypeMirror> actualTypes) {"
        self.javaMethod6 = " public JMethod implementMethod(GeneratedClassHolder holder, List<ExecutableElement> methods, String methodName, String returnType, String... parameterTypes) {"
        self.javaMethod7 = "ProgrammerInterview pInstance = new    ProgrammerInterview() {\npublic void read() {"

        c_info = ConfigInfo("../util/javatest.ini")
        self.testChunk2 = logChunk.logChunk("", "Java", c_info)

        #Read in the block tests
        self.chunkb1 = logChunk.logChunk(self.readHelper("testfiles/Block/testChunk1.txt"), "Java", c_info)
        self.chunkb2 = logChunk.logChunk(self.readHelper("testfiles/Block/testChunk2.txt"), "Java", c_info)
        self.chunkb3 = logChunk.logChunk(self.readHelper("testfiles/Block/testChunk3.txt"), "Java", c_info)
        self.chunkb4 = logChunk.logChunk(self.readHelper("testfiles/Block/testChunk4.txt"), "Java", c_info)
        self.chunkb5 = logChunk.logChunk(self.readHelper("testfiles/Block/testChunk5.txt"), "Java", c_info)
        self.chunkb6 = logChunk.logChunk(self.readHelper("testfiles/Block/testChunk6.txt"), "Java", c_info)
        self.chunkb7 = logChunk.logChunk(self.readHelper("testfiles/Block/testChunk7.txt"), "Java", c_info)
        self.chunkb8 = logChunk.logChunk(self.readHelper("testfiles/Block/testChunk8.txt"), "Java", c_info)
        self.chunkb9 = logChunk.logChunk(self.readHelper("testfiles/Block/testChunk9.txt"), "Java", c_info)
        self.chunkb10 = logChunk.logChunk(self.readHelper("testfiles/Block/testChunk10.txt"), "Java", c_info)
        self.chunkb11 = logChunk.logChunk(self.readHelper("testfiles/Block/testChunk11.txt"), "Java", c_info)


    def test_FunctionNameParseJAVA(self):

        temp = self.testChunk2.langSwitch.parseFunctionName(self.javaMethod1)
        print(temp)
        self.assertTrue(temp == "createIntent", "Actual: " + temp)
        temp = self.testChunk2.langSwitch.parseFunctionName(self.javaMethod2)
        print(temp)
        self.assertTrue(temp == "post", "Actual: " + temp)
        temp = self.testChunk2.langSwitch.parseFunctionName(self.javaMethod3)
        print(temp)
        self.assertTrue(temp == "createIntent", "Actual: " + temp)
        temp = self.testChunk2.langSwitch.parseFunctionName(self.javaMethod4)
        print(temp)
        self.assertTrue(temp == "run", "Actual: " + temp)
        temp = self.testChunk2.langSwitch.parseFunctionName(self.javaMethod5)
        print(temp)
        self.assertTrue(temp == "typeBoundsToJClass", "Actual: " + temp)
        temp = self.testChunk2.langSwitch.parseFunctionName(self.javaMethod6)
        print(temp)
        self.assertTrue(temp == "implementMethod", "Actual: " + temp)
        temp = self.testChunk2.langSwitch.parseFunctionName(self.javaMethod7)
        print(temp)
        self.assertTrue(temp == "read", "Actual: " + temp)



    def test_parseText_Block1(self):

        self.chunkb1.parseText()
        funcList = self.chunkb1.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 2)

        self.assertTrue(funcList[0].method=="foo")
        self.assertTrue(funcList[0].total_add == 2)
        self.assertTrue(funcList[0].total_del == 1)
        testDict= {'throw Adds': 0, 'catch Dels': 0, 'try Adds': 0, 'try Dels': 1, 'exception Dels': 0, 'raise Adds': 0, 'catch Adds': 1, 'finally Dels': 0, 'finally Adds': 0, 'throw Dels': 0, 'exception Adds': 0, 'raise Dels': 0, 'for Adds': 0,'for Dels': 0,'while Adds': 0,'while Dels': 0}


        self.assertEqual(testDict,funcList[0].keywordDictionary)
        self.assertTrue(funcList[1].method=="foo00022")
        self.assertTrue(funcList[1].total_add == 4)
        self.assertTrue(funcList[1].total_del == 2)
        testDict= {'throw Adds': 0, 'catch Dels': 0, 'try Adds': 1, 'try Dels': 1, 'exception Dels': 0, 'raise Adds': 0, 'catch Adds': 1, 'finally Dels': 0, 'finally Adds': 0, 'throw Dels': 0, 'exception Adds': 0, 'raise Dels': 0, 'for Adds': 0,'for Dels': 0,'while Adds': 0,'while Dels': 0}

        self.assertEqual(testDict, funcList[1].keywordDictionary)

    def test_parseText_Block2(self): #ISSUE: the current cannot assign values to multiple blocks.

        self.chunkb2.parseText()
        funcList = self.chunkb2.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 2)

        self.assertTrue(funcList[0].method=="getAccounts")
        self.assertTrue(funcList[0].total_add == 1)
        self.assertTrue(funcList[0].total_del == 2)
        testdict= {'throw Adds': 0, 'catch Dels': 0, 'try Adds': 0, 'try Dels': 0, 'exception Dels': 0, 'raise Adds': 0, 'catch Adds': 0, 'finally Dels': 0, 'finally Adds': 0, 'throw Dels': 0, 'exception Adds': 0, 'raise Dels': 0, 'for Adds': 0,'for Dels': 0,'while Adds': 0,'while Dels': 0}
        self.assertEqual(testdict,funcList[0].keywordDictionary)

        self.assertTrue(funcList[1].method=="getAccount")
        self.assertTrue(funcList[1].total_add == 6)
        self.assertTrue(funcList[1].total_del == 2)
        testdict={'throw Adds': 1, 'catch Dels': 0, 'try Adds': 3, 'try Dels': 2, 'exception Dels': 0, 'raise Adds': 0, 'catch Adds': 4, 'finally Dels': 0, 'finally Adds': 0, 'throw Dels': 0, 'exception Adds': 2, 'raise Dels': 0, 'for Adds': 0,'for Dels': 0,'while Adds': 2,'while Dels': 2}
        self.assertEqual(testdict,funcList[1].keywordDictionary)

    def test_parseText_Block3(self):

        self.chunkb3.parseText()
        funcList = self.chunkb3.functions

        #self.debugFunctions(funcList)

        self.assertTrue(len(funcList) == 1)
        self.assertTrue(funcList[0].method=="ReflectiveProperty")
        self.assertTrue(funcList[0].total_add == 8)
        self.assertTrue(funcList[0].total_del == 2)
        testdict= {'throw Adds': 0, 'catch Dels': 1, 'try Adds': 8, 'try Dels': 2, 'exception Dels': 0, 'raise Adds': 0, 'catch Adds': 4, 'finally Dels': 0, 'finally Adds': 0, 'throw Dels': 0, 'exception Adds': 0, 'raise Dels': 0, 'for Adds': 0,'for Dels': 0,'while Adds': 0,'while Dels': 0}

        self.assertEqual(testdict,funcList[0].keywordDictionary)

    def test_parseText_Block4(self):

        self.chunkb4.parseText()
        funcList = self.chunkb4.functions
        # self.debugFunctions(funcList)

        self.assertTrue(len(funcList) == 1)
        self.assertTrue(funcList[0].method=="setHandle")
        self.assertTrue(funcList[0].total_add == 1)
        self.assertTrue(funcList[0].total_del == 1)
        testdict= {'throw Adds': 0, 'catch Dels': 0, 'try Adds': 0, 'try Dels': 0, 'exception Dels': 0, 'raise Adds': 0, 'catch Adds': 0, 'finally Dels': 0, 'finally Adds': 0, 'throw Dels': 0, 'exception Adds': 0, 'raise Dels': 0, 'for Adds': 0,'for Dels': 0,'while Adds': 0,'while Dels': 0}
        self.assertEqual(testdict,funcList[0].keywordDictionary)

    def test_parseText_Block5(self):

        self.chunkb5.parseText()
        funcList = self.chunkb5.functions
        self.debugFunctions(funcList)


        self.assertTrue(len(funcList) == 2)
        self.assertTrue(funcList[0].method=="copy")
        self.assertTrue(funcList[0].total_add == 19)
        self.assertTrue(funcList[0].total_del == 5)

        testdict= {'throw Adds': 0, 'catch Dels': 0, 'try Adds': 0, 'try Dels': 0, 'exception Dels': 0, 'raise Adds': 0, 'catch Adds': 0, 'finally Dels': 0, 'finally Adds': 0, 'throw Dels': 0, 'exception Adds': 1, 'raise Dels': 0, 'for Adds': 0,'for Dels': 0,'while Adds': 0,'while Dels': 0}

        self.assertEqual(testdict,funcList[0].keywordDictionary)

        self.assertTrue(funcList[1].method==NON_FUNC) #The add del count here is a bit off due to the way we change code that has been uncommented
        testdict= {'throw Adds': 0, 'catch Dels': 0, 'try Adds': 0, 'try Dels': 0, 'exception Dels': 0, 'raise Adds': 0, 'catch Adds': 0, 'finally Dels': 0, 'finally Adds': 0, 'throw Dels': 0, 'exception Adds': 0, 'raise Dels': 0, 'for Adds': 0,'for Dels': 0,'while Adds': 0,'while Dels': 0}

        self.assertEqual(testdict,funcList[1].keywordDictionary)

    def test_parseText_Block6(self):

        self.chunkb6.parseText()
        funcList = self.chunkb6.functions
        # self.debugFunctions(funcList)

        self.assertTrue(len(funcList) == 1)


        self.assertTrue(funcList[0].method=="init")
        self.assertTrue(funcList[0].total_add == 0)
        self.assertTrue(funcList[0].total_del == 1)
        testdict= {'throw Adds': 0, 'catch Dels': 1, 'try Adds': 0, 'try Dels': 0, 'exception Dels': 1, 'raise Adds': 0, 'catch Adds': 0, 'finally Dels': 0, 'finally Adds': 0, 'throw Dels': 1, 'exception Adds': 0, 'raise Dels': 0, 'for Adds': 0,'for Dels': 0,'while Adds': 0,'while Dels': 0}

        self.assertEqual(testdict,funcList[0].keywordDictionary)

    def test_parseText_Block7(self): #Need to update expected result (Question, we seem to not count the } at end of block?)

        self.chunkb7.parseText()
        funcList = self.chunkb7.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 1)
        self.assertTrue(funcList[0].method=="onCreateLoader")
        self.assertTrue(funcList[0].total_add == 2)
        self.assertTrue(funcList[0].total_del == 7)

        testdict= {'throw Adds': 0, 'catch Dels': 4, 'try Adds': 0, 'try Dels': 2, 'exception Dels': 1, 'raise Adds': 0, 'catch Adds': 0, 'finally Dels': 0, 'finally Adds': 0, 'throw Dels': 0, 'exception Adds': 1, 'raise Dels': 0, 'for Adds': 0,'for Dels': 0,'while Adds': 0,'while Dels': 0, 'for Adds': 0,'for Dels': 0,'while Adds': 0,'while Dels': 0, 'for Adds': 0,'for Dels': 0,'while Adds': 0,'while Dels': 0}

        self.assertEqual(testdict,funcList[0].keywordDictionary)


    def test_parseText_Block8(self): #Need to update expected result (Question, we seem to not count the } at end of block?)

        self.chunkb8.parseText()
        funcList = self.chunkb8.functions
        #self.debugFunctions(funcList)

        self.assertTrue(len(funcList) == 1)
        self.assertTrue(funcList[0].method=="getAuthToken")
        self.assertTrue(funcList[0].total_add == 2)
        self.assertTrue(funcList[0].total_del == 2)
        testdict= {'throw Adds': 1, 'catch Dels': 1, 'try Adds': 1, 'try Dels': 1, 'exception Dels': 1, 'raise Adds': 0, 'catch Adds': 2, 'finally Dels': 0, 'finally Adds': 0, 'throw Dels': 0, 'exception Adds': 2, 'raise Dels': 0, 'for Adds': 0,'for Dels': 0,'while Adds': 0,'while Dels': 0}
        self.assertEqual(testdict,funcList[0].keywordDictionary)


    def test_parseText_Block9(self):

        self.chunkb9.parseText()
        funcList = self.chunkb9.functions
        #self.debugFunctions(funcList)

        self.assertTrue(len(funcList) == 1)

        self.assertTrue(funcList[0].method=="getAuthToken")
        self.assertTrue(funcList[0].total_add == 2)
        self.assertTrue(funcList[0].total_del == 2)
        testdict= {'throw Adds': 1, 'catch Dels': 1, 'try Adds': 0, 'try Dels': 0, 'exception Dels': 1, 'raise Adds': 0, 'catch Adds': 2, 'finally Dels': 0, 'finally Adds': 0, 'throw Dels': 0, 'exception Adds': 2, 'raise Dels': 0, 'for Adds': 0,'for Dels': 0,'while Adds': 0,'while Dels': 0}

        self.assertEqual(testdict,funcList[0].keywordDictionary)


    def test_parseText_Block10(self):

        self.chunkb10.parseText()
        funcList = self.chunkb10.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 1)


        self.assertTrue(funcList[0].method=="getToken")
        self.assertTrue(funcList[0].total_add == 8)
        self.assertTrue(funcList[0].total_del == 5)
        testdict= {'throw Adds': 0, 'catch Dels': 0, 'try Adds': 0, 'try Dels': 0, 'exception Dels': 0, 'raise Adds': 0, 'catch Adds': 0, 'finally Dels': 0, 'finally Adds': 0, 'throw Dels': 0, 'exception Adds': 0, 'raise Dels': 0, 'for Adds': 4,'for Dels': 5,'while Adds': 4,'while Dels': 0}

        self.assertEqual(testdict,funcList[0].keywordDictionary)

    def test_parseText_Block11(self):

        self.chunkb11.parseText()
        funcList = self.chunkb11.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 1)


        self.assertTrue(funcList[0].method=="blockTest")
        self.assertTrue(funcList[0].total_add == 1)
        self.assertTrue(funcList[0].total_del == 1)
        testdict= {'throw Adds': 0, 'catch Dels': 0, 'try Adds': 1, 'try Dels': 1, 'exception Dels': 0, 'raise Adds': 0, 'catch Adds': 0, 'finally Dels': 0, 'finally Adds': 0, 'throw Dels': 0, 'exception Adds': 0, 'raise Dels': 0, 'for Adds': 0,'for Dels': 0,'while Adds': 0,'while Dels': 0}

        self.assertEqual(testdict,funcList[0].keywordDictionary)


if __name__=="__main__":
    unittest.main()
