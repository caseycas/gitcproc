import sys
import os
import yaml #PyYAML must be installed
import languageSwitcher
import CPlusPlusLanguageSwitcher
import CLanguageSwitcher
import JavaLanguageSwitcher
import PythonLanguageSwitcher
from UnsupportedLanguageException import *

sys.path.append("../util")

from Util import supportedLanguages

class LanguageSwitcherFactory:
    extMap = {}

    @staticmethod
    def loadLanguageMap(langFile = "../../Resources/languages.yml"):
        with open(langFile, 'r') as f:
            LanguageSwitcherFactory.extMap = yaml.safe_load(f)

    #Create a new language switcher of the correct type.
    @staticmethod
    def createLS(language):
        if(LanguageSwitcherFactory.extMap == {}):
            LanguageSwitcherFactory.loadLanguageMap("../../Resources/languages.yml")

        return LanguageSwitcherFactory.determineLanguage(language)

    #String -> String
    #Given either a language name or a file extension for a language, return a normalized language string
    #to use
    @staticmethod
    def determineLanguage(language): #Replace these with tokens?
        language = language.strip()
        #Check for names
        if(language.lower() == "c++" or language.lower() in LanguageSwitcherFactory.extMap["C++"]["extensions"]):
            return CPlusPlusLanguageSwitcher.CPlusPlusLanguageSwitcher(set(LanguageSwitcherFactory.extMap["C++"]["extensions"]))
        elif(language.lower() == "c" or language.lower() in LanguageSwitcherFactory.extMap["C"]["extensions"]):
            return CLanguageSwitcher.CLanguageSwitcher(set(LanguageSwitcherFactory.extMap["C"]["extensions"]))
        elif(language.lower() == "java" or language.lower() in LanguageSwitcherFactory.extMap["Java"]["extensions"]):
            return JavaLanguageSwitcher.JavaLanguageSwitcher(set(LanguageSwitcherFactory.extMap["Java"]["extensions"]))
        elif(language.lower() == "python" or language.lower() in LanguageSwitcherFactory.extMap["Python"]["extensions"]):
            return PythonLanguageSwitcher.PythonLanguageSwitcher(set(LanguageSwitcherFactory.extMap["Python"]["extensions"]))
        else:
            print(LanguageSwitcherFactory.extMap["C"]["extensions"])
            raise UnsupportedLanguageException(language + " not yet supported.")

    @staticmethod
    def getExtensions(languages):
        '''
        Given some languages, return the set of extensions associated with them.  If no languages 
        are given or none in the set are recognized, return the extensions for all recognized languages.
        If only a portion are recognized, return the set of extensions for just these languages.
        '''
        extensions = set()
        for l in languages:
            try:
                extensions.update(LanguageSwitcherFactory.createLS(l).getExtensions())
            except UnsupportedLanguageException: #skip unrecognized languages
                pass

        if (len(extensions) == 0):
            return getExtensions(supportedLanguages)
        else:
            return extensions

