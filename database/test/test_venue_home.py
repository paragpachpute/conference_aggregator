from unittest import TestCase
from database.venue_home import VenueHome
from entity.conference import Conference

class TestVenueHome(TestCase):
    def setUp(self):
        database = 'test_database'
        self.venue_home = VenueHome(database)