from unittest import TestCase
from database.conference_home import ConferenceHome
from entity.conference import Conference

class TestConferenceHome(TestCase):
    def setUp(self):
        database = 'test_database'
        self.conferenceHome = ConferenceHome(database)

    def test_venue_url(self):
        # conference = Conference('aaai', 'https://dblp.org/db/conf/aaai/', 'https://www.aaai.org/')
        conference = Conference('ijcai', 'https://dblp.org/db/conf/ijcai/', 'https://www.ijcai.org/')
        # conference = Conference('akbc', 'https://dblp.org/db/conf/akbc/')

        self.conferenceHome.store_conference(conference)

        urls = self.conferenceHome.get_conference({'name': conference.name})
        conf = urls[0]
        conf = Conference(**conf)

        self.assertEqual(conference.name, conf.name, 'Conference name not matching')
        self.assertEqual(conference.dblp_url, conf.dblp_url, 'Conference dblp_url not matching')