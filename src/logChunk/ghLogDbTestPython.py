import sys

sys.path.append("../util")
import Util
from Util import ConfigInfo
import unittest
import ghLogDb


class ghLogDbTestPython(unittest.TestCase):

    def setUp(self):
 
        c_info = ConfigInfo("../util/pytest.ini")
        self.testCommit1 = ghLogDb.ghLogDb("testfiles/ghLogDbTestPython/TestCommit1.txt",c_info)
        self.testCommit2 = ghLogDb.ghLogDb("testfiles/ghLogDbTestPython/TestCommit2.txt",c_info)
     
    def test_Commit1(self):
        self.testCommit1.processLog()
        shas = self.testCommit1.shas
        self.assertTrue(shas[0].author == "James Cammarata")
        patches = shas[0].patches
        self.assertTrue(len(patches) == 1)
        for patch in patches:
            self.assertTrue(patch.language == "py")
            self.assertTrue(patch.is_test == False)

        self.assertTrue(patches[0].file_name == "lib/ansible/executor/task_executor.py")
        methods = patches[0].methods
        self.assertTrue(len(methods) == 1)

        self.assertTrue(methods[0].method == "_get_loop_items")
        self.assertTrue(methods[0].total_add == 1)
        self.assertTrue(methods[0].total_del == 1)

        testDict = {'print Adds': 0, 'print Dels': 0, 'if Dels': 1, 'if Adds': 1}
        self.assertEqual(testDict,methods[0].keywordDictionary)

    def test_Commit2(self): 
        self.testCommit2.processLog()
        shas = self.testCommit2.shas
        self.assertTrue(shas[0].author == "David Chan")
        patches = shas[0].patches
        self.assertTrue(len(patches) == 1)
        for patch in patches:
            self.assertTrue(patch.language == "py")
            self.assertTrue(patch.is_test == False)

        self.assertTrue(patches[0].file_name == "contrib/inventory/spacewalk.py")
        methods = patches[0].methods
        self.assertTrue(len(methods) == 1)

        self.assertTrue(methods[0].method == "GITCPROC_NON_FUNCTION")
        self.assertTrue(methods[0].total_add == 1)
        self.assertTrue(methods[0].total_del == 1)

        testDict = {'print Adds': 0, 'print Dels': 0, 'if Dels': 1, 'if Adds': 1}
        self.assertEqual(testDict,methods[0].keywordDictionary)

if __name__=="__main__":
    unittest.main()
