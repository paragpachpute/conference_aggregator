from unittest import TestCase
from .venue_home import VenueHome
from entity.conference import VenueUrl

class TestVenueHome(TestCase):
    def setUp(self):
        database = 'test_database'
        self.venueHome = VenueHome(database)

    def test_venue_url(self):
        venue_url = VenueUrl('aaai', 'https://dblp.org/db/conf/aaai/')
        self.venueHome.store_venue_url(venue_url)

        urls = self.venueHome.get_venue_url({})
        url = urls[0]

        self.assertEqual(venue_url.name, url['name'], 'Venue name not matching')
        self.assertEqual(venue_url.url, url['url'], 'Venue url not matching')