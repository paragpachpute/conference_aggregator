from unittest import TestCase
from bs4 import BeautifulSoup
from .venue_parser import VenueParser

class TestVenueParser(TestCase):
    def setUp(self) -> None:
        self.venueParser = VenueParser()

    def test_get_venues(self):
        with open('dblp/dblp_aaai.htm') as document:
            soup = BeautifulSoup(document.read(), features="html.parser")
            h2s = soup.find_all('h2')

            venues = self.venueParser.get_venues(h2s)
            self.assertEqual(34, len(venues))