from .connection_utils import get_database

class DeadlineHome:

    def __init__(self, database_name='test_database'):
        self.database_name = database_name

        deadline_collection_name = 'deadlines'

        self.db = get_database(self.database_name)
        self.deadline_collection = self.db[deadline_collection_name]

    def store_many_deadlines(self, deadlines):
        for d in deadlines:
            self.store_deadline(d)

    def store_deadline(self, deadline):
        deadline['_id'] = deadline['title']
        criteria = {"_id": deadline['_id']}
        self.deadline_collection.replace_one(criteria, deadline, upsert=True)

    def get_deadline(self, criteria={}):
        return self.deadline_collection.find(criteria)
