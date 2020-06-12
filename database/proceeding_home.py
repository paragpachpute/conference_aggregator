from .connection_utils import get_database

class ProceedingHome:

    def __init__(self, database_name='test_database'):
        self.database_name = database_name

        proceeding_collection_name = 'proceeding'

        self.db = get_database(self.database_name)
        self.proceeding_collection = self.db[proceeding_collection_name]

    # Dumps the proceeding object into the database
    def store_proceeding(self, proceeding):
        criteria = {"_id" : proceeding._id}
        self.proceeding_collection.replace_one(criteria, vars(proceeding), upsert=True)

    # Dumps the venue objects into the database
    def store_many_proceedings(self, proceeding_list):
        for p in proceeding_list:
            self.store_proceeding(p)

    def get_proceedings(self, criteria={}):
        return self.proceeding_collection.find(criteria)