from parser.dblp.venue_parser import VenueParser
from database.venue_home import VenueHome
from database.proceeding_home import ProceedingHome

database = 'test_database'
parser = VenueParser()
venueHome = VenueHome(database)
proceedingHome = ProceedingHome(database)

with open('./../parser/dblp/dblp_aaai.htm') as document:
    venues = parser.parse(document.read())
    venueHome.store_many_venues(venues)

with open('./../parser/dblp/proceeding.xml') as xml:
    proceeding = parser.get_proceeding(xml.read())
    proceedingHome.store_proceeding(proceeding)