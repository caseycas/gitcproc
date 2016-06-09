import yaml #PyYAML must be installed
import scopeTracker
import BracketScopeTracker
import PythonScopeTracker
from UnsupportedLanguageException import *

BracketLanguages = ["C", "C++", "Java"]
IndentLanguages = ["Python"]

class ScopeTrackerFactory:
    @staticmethod
    def createST(languageSwitcher, c_info):
        """
        Create a new scope tracker of the correct type.
        """
        lang = languageSwitcher.getLanguage()
        if(lang in BracketLanguages):
            return BracketScopeTracker.BracketScopeTracker(lang, c_info)
        elif(lang in IndentLanguages):
            return PythonScopeTracker.PythonScopeTracker(lang, c_info)
        else:
            raise UnsupportedLanguageException(lang + " is not yet supported.")
        