from .connection_utils import get_database

class ConferenceHome:

    def __init__(self, database_name):
        self.database_name = database_name

        conference_collection_name = 'conference'

        self.db = get_database(self.database_name)
        self.conference_collection = self.db[conference_collection_name]

    # Dumps the venue objects into the database
    def store_many_conference(self, conference_list):
        for c in conference_list:
            self.store_conference(c)

    # Dumps the conference object into the database
    def store_conference(self, conference):
        criteria = {"_id": conference._id}
        self.conference_collection.replace_one(criteria, vars(conference), upsert=True)

    def get_conference(self, criteria={}):
        return self.conference_collection.find(criteria)
