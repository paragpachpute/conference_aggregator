from .connection_utils import get_database


class ErrorQueueHome:

    def __init__(self, database_name='test_database'):
        self.database_name = database_name

        error_queue_collection_name = 'error_queue'

        self.db = get_database(self.database_name)
        self.error_queue_collection = self.db[error_queue_collection_name]

    def store_error_queue_item(self, item):
        criteria = {"_id" : item._id}
        self.error_queue_collection.replace_one(criteria, vars(item), upsert=True)

    def store_many_error_queue_items(self, item_list):
        for v in item_list:
            self.store_error_queue_item(v)

    def get_error_queue_item(self, criteria={}):
        return self.error_queue_collection.find(criteria)

    def delete_error_queue_item(self, criteria={}):
        self.error_queue_collection.delete_one(criteria)
