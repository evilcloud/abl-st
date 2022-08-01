from deta import Deta
import os

# DETA_KEY = os.environ.get("DETA")
DETA_KEY = "a01urg15_fgGFQpkCSU2GTjWzK86H5rF8XU9NKF2n"
CLIENT = Deta(DETA_KEY)


class Detadb:
    def __init__(self, dbname):
        self.db = CLIENT.Base(dbname)

    def fetch(self):
        self.entries = self.db.fetch()


DB_NAME = "ABEL_MINING"
a = Detadb(DB_NAME)
a.fetch().items
