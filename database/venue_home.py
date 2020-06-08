from .connection_utils import get_database

class VenueHome:

    def __init__(self, database_name):
        self.database_name = database_name

        venue_collection_name = 'venue'
        venue_url_collection_name = 'venue_url'

        self.db = get_database(self.database_name)
        self.venue_collection = self.db[venue_collection_name]
        self.venue_url_collection = self.db[venue_url_collection_name]

    # Dumps the venue object into the database
    def store_venue(self, venue):
        criteria = {"_id" : venue._id}
        self.venue_collection.replace_one(criteria, vars(venue), upsert=True)

    # Dumps the venue objects into the database
    def store_many_venues(self, venue_list):
        for v in venue_list:
            self.store_venue(v)

    def get_venue(self, criteria):
        return self.venue_collection.find(criteria)

    # Dumps the venue url into the database
    def store_venue_url(self, obj):
        self.venue_url_collection.insert_one(vars(obj))

    def get_venue_url(self, criteria={}):
        return self.venue_url_collection.find(criteria)
