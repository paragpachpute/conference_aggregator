from unittest import TestCase

from .conference_list_parser import ConferenceListParser


class TestVenueParser(TestCase):
    def setUp(self) -> None:
        self.conference_list_parser = ConferenceListParser()

    def test_get_venues(self):
        with open('dblp/conference_list.htm') as document:
            confs = self.conference_list_parser.parse(document.read())
            self.assertEqual(100, len(confs))