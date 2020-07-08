from unittest import TestCase

from parser.dblp.venue_list_parser import VenueListParser


class TestVenueListParser(TestCase):
    def setUp(self) -> None:
        self.venue_list_parser = VenueListParser()

    def test_get_venues(self):
        with open('../resources/conference_list.htm') as document:
            confs = self.venue_list_parser.parse(document.read())
            self.assertEqual(100, len(confs))