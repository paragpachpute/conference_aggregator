from parser.dblp.venue_parser import VenueParser
from database.venue_home import VenueHome
from database.proceeding_home import ProceedingHome
from database.conference_home import ConferenceHome
from database.research_paper_home import ResearchPaperHome
from database.error_queue_home import ErrorQueueHome
import json
import urllib.request
import logging
import os
from entity.conference import Conference
from entity.proceeding import Proceeding
from entity.error_queue_item import ErrorQueueItem


log = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def fetch_proceeding_info(conference_name, venues, parser, errorQueueHome):
    proceedings = []
    proceeding_xml_base_url = "https://dblp.org/rec/xml/"
    for venue in venues:
        for proceeding_id in venue.proceedings:
            try:
                url = proceeding_xml_base_url + proceeding_id + ".xml"
                log.debug("Fetching from proceeding url: {}".format(url))
                proceeding = get_proceeding_info_from_url(conference_name, url, parser)
                proceedings.append(proceeding)
            except Exception as ex:
                errorQueueHome.store_error_queue_item(ErrorQueueItem(ErrorQueueItem.TYPE_PROCEEDING_INFO, url))
                log.error("Parsing error for proceeding_id {} of conference {}. Error: {}".format(proceeding_id, conference_name, ex))
                pass
    return proceedings

def get_proceeding_info_from_url(conference_name, url, parser):
    xml = urllib.request.urlopen(url)
    proceeding = parser.get_proceeding(conference_name, xml.read())
    return proceeding


def get_venues_from_url(url, parser):
    document = urllib.request.urlopen(url)
    venues = parser.parse(conference.name, document.read())
    return venues


def get_research_papers_from_url(url):
    json_doc = urllib.request.urlopen(url)
    return json.loads(json_doc.read())


if __name__ == '__main__':

    database = 'test_database'
    parser = VenueParser()
    venueHome = VenueHome(database)
    proceedingHome = ProceedingHome(database)
    conferenceHome = ConferenceHome(database)
    researchPaperHome = ResearchPaperHome(database)
    errorQueueHome = ErrorQueueHome(database)

    # TODO think should we add url in every entity that states the url from which it was fetched
    conferences = conferenceHome.get_conference()
    for c in conferences:
        conference = Conference(**c)
        log.info('Started processing: ' + conference.name)

        if conference.name is not 'akbc':
            try:
                venues = get_venues_from_url(conference.dblp_url, parser)
                log.debug("Fetched {} venues for conference {}".format(len(venues), conference.name))
                venueHome.store_many_venues(venues)

                proceedings = fetch_proceeding_info(conference.name, venues, parser, errorQueueHome)
                proceedingHome.store_many_proceedings(proceedings)
            except Exception as ex:
                errorQueueHome.store_error_queue_item(ErrorQueueItem(ErrorQueueItem.TYPE_VENUE, conference.dblp_url))
                log.error("Parsing error for venues of conference {}. Error: {}".format(conference.name, ex))
                pass

    # TODO repeat this for each conference
    proceedings = proceedingHome.get_proceedings({"conference_name": "ijcai"})
    for p in proceedings:
        proceeding = Proceeding(**p)
        log.info("Started processing for " + p['title'])

        # TODO generate link to handle more than 1000 records

        # https://dblp.org/search/publ/api?q=toc:db/conf/ijcai/ijcai2017.bht:&h=500&f=500&format=json

        base_url = "https://dblp.org/search/publ/api?q=toc:"
        url = base_url + p['dblp_url'].split(".html")[0] + ".bht"
        url += ":&h=1000&format=json"
        print(url)

        try:
            obj = get_research_papers_from_url(url)

            if 'result' in obj and 'hits' in obj['result'] and 'hit' in obj['result']['hits']:
                result = obj['result']
                hits = result['hits']
                for research_paper in hits['hit']:
                    # TODO decode html entities from the strings
                    research_paper['_id'] = research_paper['info']['title']
                    researchPaperHome.store_research_paper(research_paper)
        except Exception as ex:
            errorQueueHome.store_error_queue_item(ErrorQueueItem(ErrorQueueItem.TYPE_RESEARCH_PAPERS, url))
            log.error("Parsing error for research papers of proceeding {}".format(proceeding.proceeding_key))
            pass

