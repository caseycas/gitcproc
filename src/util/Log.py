import logging
import logging.config

def setLogger(logLevel, logFile):

	logger = logging.getLogger()

	str2log = {
	'd' : logging.DEBUG,
	'i' : logging.INFO,
	'w' : logging.WARN,
	'e' : logging.ERROR,
	'c' : logging.CRITICAL
	}

	log_level = str2log.get(logLevel,logging.WARN) #set to warning by default

	#logging.basicConfig(filename=logFile, filemode='w', level=log_level)	
	#ERROR_FORMAT = "%(levelname)s at %(asctime)s in %(funcName)s in %(filename) at line %(lineno)d: %(message)s"
	DEBUG_FORMAT = "%(filename)s:%(lineno)d : %(message)s"
	ERROR_FORMAT = DEBUG_FORMAT

	LOG_CONFIG = {
		'version' : 1, 
		'formatters' : {'error': {'format':ERROR_FORMAT}, 'debug':{'format':DEBUG_FORMAT}}, 
		'handlers' : 
			{'console' : { 'class':'logging.StreamHandler', 'formatter':'debug', 'level':logging.ERROR },
			'file' : { 'class':'logging.FileHandler', 'filename':logFile, 'formatter':'error', 'level':logging.DEBUG}},
		'root':{'handlers':('console', 'file'), 'level': log_level}
		}

	logging.config.dictConfig(LOG_CONFIG)
