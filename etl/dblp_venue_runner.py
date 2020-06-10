from parser.dblp.venue_parser import VenueParser
from database.venue_home import VenueHome
from database.proceeding_home import ProceedingHome
from database.conference_home import ConferenceHome
from database.research_paper_home import ResearchPaperHome
import json
import urllib.request


database = 'test_database'
parser = VenueParser()
venueHome = VenueHome(database)
proceedingHome = ProceedingHome(database)
conferenceHome = ConferenceHome(database)
researchPaperHome = ResearchPaperHome(database)

# conferences = conferenceHome.get_conference()
# for c in conferences:
#     print(c)
#     document = urllib.request.urlopen(c['url'])
#     venues, proceedings = parser.parse(c['name'], document.read())
#     print(len(venues), len(proceedings))
#     venueHome.store_many_venues(venues)
#     proceedingHome.store_many_proceedings(proceedings)

# with open('./../parser/dblp/dblp_aaai.htm') as document:
#     # TODO explore from bunch import bunchify for converting it back to object
#     venues = parser.parse(c['name'], document.read())
#     venueHome.store_many_venues(venues)
#
# with open('./../parser/dblp/proceeding.xml') as xml:
#     proceeding = parser.get_proceeding(c['name'], xml.read())
#     proceedingHome.store_proceeding(proceeding)
#
#
proceedings = proceedingHome.get_proceedings({"conference_name" : "ijcai"})
for p in proceedings:
    print("Started processing for", p['_id'])

    # TODO generate link to handle more than 1000 records
    base_url = "https://dblp.org/search/publ/api?q=toc:"
    url = base_url + p['dblp_url'].split(".html")[0] + ".bht"
    url += ":&h=1000&format=json"

    json_doc = urllib.request.urlopen(url)
    obj = json.loads(json_doc.read())

    if 'result' in obj and 'hits' in obj['result'] and 'hit' in obj['result']['hits']:
        result = obj['result']
        hits = result['hits']
        for research_paper in hits['hit']:
            # TODO decode html entities from the strings
            research_paper['_id'] = research_paper['info']['title']
            researchPaperHome.store_research_paper(research_paper)

#
# with open('./../parser/dblp/proceeding_papers.json') as json_file:
#     obj = json.loads(json_file.read())
#     if 'result' in obj and 'hits' in obj['result'] and 'hit' in obj['result']['hits']:
#         result = obj['result']
#         hits = result['hits']
#         for research_paper in hits['hit']:
#             research_paper['_id'] = research_paper['info']['title']
#             researchPaperHome.store_research_paper(research_paper)

