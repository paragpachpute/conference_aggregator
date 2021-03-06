from util.utils import verbose_print
from pymongo import MongoClient

def get_database(name, verbose=True):
    verbose_print("Connecting to database: " + name, verbose)

    # Ideally thess values should come from a properties/config file
    client = MongoClient('localhost', 27017)
    db = client[name]
    return db


