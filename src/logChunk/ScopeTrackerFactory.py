import yaml #PyYAML must be installed
import scopeTracker
import BracketScopeTracker
import IndentScopeTracker
from UnsupportedLanguageException import *

BracketLanguages = ["C", "C++", "Java"]
IndentLanguages = ["Python"]

class ScopeTrackerFactory:
    @staticmethod
    def createST(languageSwitcher):
        """
        Create a new scope tracker of the correct type.
        """
        lang = languageSwitcher.getLanguage()
        if(lang in BracketLanguages):
            return BracketScopeTracker.BracketScopeTracker(lang)
        elif(lang in IndentLanguages):
            return IndentScopeTracker.IndentScopeTracker(lang)
        else:
            raise UnsupportedLanguageException(language + " is not yet supported.")
        