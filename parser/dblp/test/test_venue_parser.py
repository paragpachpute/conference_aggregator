from unittest import TestCase

from bs4 import BeautifulSoup

from parser.dblp.venue_parser import VenueParser


class TestVenueParser(TestCase):
    def setUp(self) -> None:
        self.venueParser = VenueParser()

    def test_get_venues(self):
        with open('../resources/dblp_aaai.htm') as document:
            soup = BeautifulSoup(document.read(), features="html.parser")
            h2s = soup.find_all('h2')

            venues = []
            for h2 in h2s:
                venue = self.venueParser.get_venue("test", h2)
                venues.append(venue)
            self.assertEqual(34, len(venues))