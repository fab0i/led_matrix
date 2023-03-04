from tinydb import TinyDB, Query

DB_FILE_PATH = 'main_db.json'


class BaseDB:
    def __init__(self, table=None):
        self.db = TinyDB(DB_FILE_PATH)
        self.table = self.db.table(table)
        self.q = Query()
        self.query = self.q

    def insert(self, doc):
        self.table.insert(doc)

    def search(self, condition):
        return self.table.search(condition)

class JobsDB(BaseDB):
    def __init__(self):
        BaseDB.__init__(self, table='jobs')

    def get_incoming_alerts(self):
        return self.search(self.q.job == 'alert' and self.q.soon <= 1)



class ImagesDB(BaseDB):
    def __init__(self):
        BaseDB.__init__(self, table='images')
