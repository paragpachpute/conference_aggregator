from unittest import TestCase

from database.proceeding_home import ProceedingHome
from database.venue_home import VenueHome
from entity.proceeding import Proceeding
from entity.venue import Venue
from parser.dblp.venue_parser import VenueParser
from etl.dblp_venue_runner import fetch_proceeding_info


class TestDBLPVenueRunner(TestCase):
    def setUp(self) -> None:
        self.parser = VenueParser()
        self.venue_home = VenueHome()
        self.proceeding_home = ProceedingHome()

    def test_venue_parse_store(self):
        conference_name = 'aaai'
        with open('./../parser/dblp/dblp_aaai.htm') as document:
            venues = self.parser.parse(conference_name, document.read())
            self.venue_home.store_many_venues(venues)

            venues = self.venue_home.get_venue({"year": "1993"})
            venue = Venue(**venues[0])
            self.assertEqual("11th AAAI 1993: Washington, DC", venue.title)

    def test_proceeding_parse_store(self):
        conference_name = 'aaai'
        with open('./../parser/dblp/proceeding.xml') as xml:
            proceeding = self.parser.get_proceeding(conference_name, xml.read())
            self.proceeding_home.store_proceeding(proceeding)

            proceedings = self.proceeding_home.get_proceedings({"conference_name": conference_name})
            proceeding = Proceeding(**proceedings[0])
            self.assertEqual("SafeAI@AAAI", proceeding.booktitle)

    def test_fetch_proceeding_info(self):
        conference_name = 'aaai'
        with open('./../parser/dblp/dblp_aaai.htm') as document:
            venues = self.parser.parse(conference_name, document.read())
            self.venue_home.store_many_venues(venues)
            proceedings = fetch_proceeding_info(conference_name, venues, self.parser)
            self.assertEqual(113, len(proceedings))
