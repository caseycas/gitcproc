# import psycopg2
import logging
import sys

from Config import Config

class DatabaseCon:
    def __init__(self, db, dbUser, dbHost, dbPort, passwrd):
        print "Going to connect to database %s in server %s, for user %s" % (db, dbHost, dbUser)
        #passwrd = raw_input("Please enter password..\n")
        # self.conn = psycopg2.connect(database=db, user=dbUser, host=dbHost, port=dbPort,password=passwrd)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def insert(self, sql_command):
        logging.debug("Executing SQL command = %s\n", sql_command)
        #print("Executing SQL command = %s\n", sql_command)
        cur = self.conn.cursor()
        try:
            cur.execute(sql_command)
        except psycopg2.IntegrityError:
            print "Copy already exists."
            print(sql_command)
            self.conn.rollback()
            return
        except:
            print "!!! Error"
            print(sql_command)
        #  #raise
            return

    def execute(self, sql_command):
        logging.debug("Executing SQL command = %s\n", sql_command)
        cur = self.conn.cursor()
        try:
            cur.execute(sql_command)
            rows = cur.fetchall()
            return rows
        except:
            print(sql_command)
            raise


    def test(config_file):
        cfg = Config(config_file)
        db_config = cfg.ConfigSectionMap("Database")
        print "Database configuration = %r\n", db_config

        dbCon = DatabaseCon(db_config['database'], db_config['user'], db_config['host'], db_config['port'], db_config['password'])

        sql_command = "SELECT language, project, min(commit_date), max(commit_date)"
        sql_command +=  " FROM " + db_config['table'] + " Where language iLike \'java\' group by language, project"

        rows = dbCon.execute(sql_command)

        for r in rows:
            print r


if __name__ == '__main__':

        if len(sys.argv) < 2:
            print "!! please give a confg file"
            sys.exit()

        test(sys.argv[1])
