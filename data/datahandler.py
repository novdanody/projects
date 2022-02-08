from utils.sqlitehandle import SQLiteHandle

class DataHandler:
    def __init__(self, tag):
        self.tag = tag

    @classmethod
    def post_process(cls, data):
        data.columns = data.columns.str.lower().str.replace(" ", "_")
        return data

    # get from local cache
    def get(self):
        pass

    # get from the source, be it API call etc
    def obtain(self):
        pass

    @classmethod
    def get_local_filename(cls):
        return cls.__name__.lower()

    def save(self, data):
        pass
