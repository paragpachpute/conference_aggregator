from parser.dblp.venue_parser import VenueParser
from database.venue_home import VenueHome
from database.proceeding_home import ProceedingHome
from database.conference_home import ConferenceHome

database = 'test_database'
parser = VenueParser()
venueHome = VenueHome(database)
proceedingHome = ProceedingHome(database)
conferenceHome = ConferenceHome(database)

conferences = conferenceHome.get_conference()
for c in conferences:
    print(c)

with open('./../parser/dblp/dblp_aaai.htm') as document:
    # TODO explore from bunch import bunchify for converting it back to object
    venues = parser.parse(c['name'], document.read())
    venueHome.store_many_venues(venues)

with open('./../parser/dblp/proceeding.xml') as xml:
    proceeding = parser.get_proceeding(c['name'], xml.read())
    proceedingHome.store_proceeding(proceeding)

proceedings = proceedingHome.get_proceedings({"conference_name" : "aaai"})
for p in proceedings:
    base_url = "https://dblp.org/search/publ/api?q=toc:"
    url = base_url + p['dblp_url'].split(".html")[0] + ".bht"
    url += ":&h=1000&format=json"
    print(url)