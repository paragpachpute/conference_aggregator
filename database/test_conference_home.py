from unittest import TestCase
from .conference_home import ConferenceHome
from entity.conference import Conference

class TestConferenceHome(TestCase):
    def setUp(self):
        database = 'test_database'
        self.conferenceHome = ConferenceHome(database)

    def test_venue_url(self):
        conference = Conference('aaai', 'https://dblp.org/db/conf/aaai/')
        self.conferenceHome.store_conference(conference)

        urls = self.conferenceHome.get_conference()
        url = urls[0]

        self.assertEqual(conference.name, url['name'], 'Conference name not matching')
        self.assertEqual(conference.url, url['url'], 'Conference url not matching')