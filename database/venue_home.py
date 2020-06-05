from .connection_utils import get_database

class VenueHome:

    def __init__(self, database_name):
        self.database_name = database_name
        collection_name = 'venue'
        self.db = get_database(self.database_name)
        self.collection = self.db[collection_name]

    # Dumps the venue object into the database
    def store(self, obj):
        self.collection.insert_one(obj)

    def get(self, criteria):
        return self.collection.find(criteria)

