import sys, os
#import psycopg2
import logging
import codecs

sys.path.append("../util")

from DatabaseCon import DatabaseCon
from Config import Config
import Util


class dumpLogs:

    def __init__(self, configFile=Util.CONFIG):

        self.cfg = Config(configFile)
        self.connectDb()
        #self.cleanDb()


    def connectDb(self):

        self.db_config = self.cfg.ConfigSectionMap("Database")
        logging.debug("Database configuration = %r\n", self.db_config)
        self.dbCon = DatabaseCon(self.db_config['database'], self.db_config['user'], \
                                 self.db_config['host'], self.db_config['port'], \
                                 self.db_config['password'])


    def cleanDb(self):

        schema = self.db_config['schema']
        response = 'y' # raw_input("Deleting database %s ?" % (self.db_config['schema']))

        schema = self.db_config['schema']
        tables = []
        tables.append(schema + "." + self.db_config['table_method_detail'])
        tables.append(schema + "." + self.db_config['table_change_summary'])

        if response.lower().startswith('y'):
            for table in tables:
                print("Deleting table %r \n" % table)
                sql_command = "DELETE FROM " + table
                self.dbCon.insert(sql_command)

        self.dbCon.commit()


    def close(self):
        self.dbCon.commit()
        self.dbCon.close()

    def dumpSummary(self, summaryStr):

        schema = self.db_config['schema']
        table = schema + "." + self.db_config['table_change_summary']

        sql_command = "INSERT INTO " + table + \
                      "(project, sha, author, commit_date, is_bug)" + \
                      " VALUES (" + summaryStr + ")"

        #print sql_command
        self.dbCon.insert(sql_command)
        self.dbCon.commit()

    def dumpMethodChanges(self, methodChange, titleString):

        schema = self.db_config['schema']
        table = schema + "." + self.db_config['table_method_detail']

        #sql_command = "INSERT INTO " + table + \
        #            "(project, sha, language, file_name, is_test, method_name, assertion_add, " + \
        #            "assertion_del, total_add, total_del)" + \
        #            "VALUES (" + methodChange + ")"

        sql_command = "INSERT INTO " + table + titleString + " VALUES (" + methodChange + ")"

        if(Util.DEBUG):
                print(sql_command)

        self.dbCon.insert(sql_command)
        self.dbCon.commit()


