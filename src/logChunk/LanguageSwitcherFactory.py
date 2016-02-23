import yaml #PyYAML must be installed
import languageSwitcher
import CPlusPlusLanguageSwitcher
import CLanguageSwitcher
import JavaLanguageSwitcher
from UnsupportedLanguageException import *

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
        #Check for names
        if(language.lower() == "c++" or language.lower() in LanguageSwitcherFactory.extMap["C++"]["extensions"]):
            return CPlusPlusLanguageSwitcher.CPlusPlusLanguageSwitcher()
        elif(language.lower() == "c" or language.lower() in LanguageSwitcherFactory.extMap["C"]["extensions"]):
            return CLanguageSwitcher.CLanguageSwitcher()
        elif(language.lower() == "java" or language.lower() in LanguageSwitcherFactory.extMap["Java"]["extensions"]):
            return JavaLanguageSwitcher.JavaLanguageSwitcher()
        elif(language.lower() == "python" or language.lower() in LanguageSwitcherFactory.extMap["Python"]["extensions"]):
            raise UnsupportedLanguageException(language + " not yet supported.")
        else:
            raise UnsupportedLanguageException(language + " not yet supported.")