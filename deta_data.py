import os
import sys
import datetime
import humanize
from numpy import block
from deta import Deta

DETA_KEY = os.environ.get("DETA", None)
if not DETA_KEY:
    print("Missing DETA environment variable")
    sys.exit(1)
print("Connecting to Detadb...", end="")
CLIENT = Deta(DETA_KEY)
print("done")


class Detadb:
    def __init__(self, dbname) -> None:
        self.db = CLIENT.Base(dbname)
        self.entries = self.db.fetch()
        self.entries.count = self.entries.count()
        if self.entries_count:
            print(
                f"Database {dbname} already exists with {self.entries_count} entries..."
            )
        else:
            print(f"Database {dbname} does not exist. Creating...")
