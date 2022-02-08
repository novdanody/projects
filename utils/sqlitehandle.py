import sqlite3
import pandas as pd
from utils.logger import logger

DB_ROOT = "/Users/NovdanoDY/projects/sqlitedb"


class SQLiteHandle:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(DB_ROOT + "/" + db_name)
        self.cursor = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.cursor is not None:
            self.cursor.close()

        self.conn.close()

    def query(self, query):
        logger.debug("Query sql: %s", query)
        result = pd.read_sql(query, self.conn)
        logger.debug("Done Query: %s", query)
        return result

    def execute(self, sql):
        self.cursor = self.conn.cursor()
        logger.debug("Execute sql: %s", sql)
        self.cursor.execute(sql)
        self.conn.commit()

    def clear(self, table_name):
        sql = "DROP TABLE %s" % table_name
        self.execute(sql)
