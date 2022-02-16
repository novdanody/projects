from data.datahandler import DataHandler
from utils.sqlitehandle import SQLiteHandle
from utils.logger import logger


class SQLiteDataHandler(DataHandler):
    def __init__(self, tag):
        self.tag = tag
        DataHandler.__init__(self, tag)

    @classmethod
    def get_local_filename(cls):
        return super(SQLiteDataHandler, cls).get_local_filename() + ".db"

    def get_table_name(self):
        return self.tag.lower().replace("/", "_")

    def get(self):
        db_name = self.get_local_filename()
        table_name = self.get_table_name()
        with SQLiteHandle(db_name) as handle:
            data = handle.query("SELECT * FROM %s" % table_name)

        return data

    def save(self, data, insertion_method='append'):
        db_name = self.get_local_filename()
        table_name = self.get_table_name()
        with SQLiteHandle(db_name) as handle:
            logger.info("Saving table %s in db %s", table_name, db_name)
            data.to_sql(table_name, handle.conn, if_exists=insertion_method, index=False)

    def clear(self):
        db_name = self.get_local_filename()
        table_name = self.get_table_name()
        with SQLiteHandle(db_name) as handle:
            handle.clear(table_name)
