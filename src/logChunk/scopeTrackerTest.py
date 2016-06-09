import unittest
import scopeTracker
import ScopeTrackerFactory
import LanguageSwitcherFactory
import sys
from chunkingConstants import *

sys.path.append("../util")

import Util
from Util import ConfigInfo

class logChunktest(unittest.TestCase):

    def setUp(self):
        self.langSwitch = LanguageSwitcherFactory.LanguageSwitcherFactory.createLS("C")
        c_info = ConfigInfo("../util/sample_conf.ini")
        self.sT = ScopeTrackerFactory.ScopeTrackerFactory.createST(self.langSwitch, c_info)

    def test_scopeOrder(self):
        line = "} catch(Exception e) {"
        output = self.sT.scopeOrder(line, ADD)
        expected = [DECREASE, INCREASE]
        self.assertTrue(output == expected, "Test 1 Actual: " + str(output))

        line = "namespace temp { func A(int x) { if (x == 1) {return 0;} else {return 1;} } }"
        output = self.sT.scopeOrder(line, ADD)
        expected = [INCREASE, INCREASE, INCREASE, DECREASE, INCREASE, DECREASE, DECREASE, DECREASE]
        self.assertTrue(output == expected, "Test 2 Actual: " + str(output) )

        line = "namespace temp { func A(int x) { "
        output = self.sT.scopeOrder(line, ADD)
        expected = [INCREASE, INCREASE]
        self.assertTrue(output == expected, "Test 3 Actual: " + str(output))

        line = "}"
        output = self.sT.scopeOrder(line, ADD)
        expected = [DECREASE]
        self.assertTrue(output == expected, "Test 4 Actual: " + str(output))

        line = "blah {}}"
        output = self.sT.scopeOrder(line, ADD)
        expected = [INCREASE, DECREASE, DECREASE]
        self.assertTrue(output == expected, "Test 5 Actual: " + str(output))

        line = "x = y;"
        output = self.sT.scopeOrder(line, ADD)
        expected = []
        self.assertTrue(output == expected, "Test 6 Actual: " + str(output))


if __name__=="__main__":
    unittest.main()