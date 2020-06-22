import json
import logging
import os
import urllib.request

from database.conference_home import ConferenceHome
from database.error_queue_home import ErrorQueueHome
from database.proceeding_home import ProceedingHome
from database.research_paper_home import ResearchPaperHome
from database.venue_home import VenueHome
from entity.conference import Conference
from entity.error_queue_item import ErrorQueueItem
from entity.proceeding import Proceeding
from parser.dblp.venue_parser import VenueParser

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
                log.error("Parsing error for proceeding_id {} of conference {}. Error: {}".format(proceeding_id,
                                                                                                  conference_name, ex))
                pass
    return proceedings


def get_proceeding_info_from_url(conference_name, url, parser):
    xml = urllib.request.urlopen(url)
    proceeding = parser.get_proceeding(conference_name, xml.read())
    return proceeding


def get_venues_from_url(url, conference_name, parser):
    document = urllib.request.urlopen(url)
    venues = parser.parse(conference_name, document.read())
    return venues


def get_research_papers_from_url(url):
    json_doc = urllib.request.urlopen(url)
    return json.loads(json_doc.read())


if __name__ == '__main__':
    database = 'test_database2'
    parser = VenueParser()
    venueHome = VenueHome(database)
    proceedingHome = ProceedingHome(database)
    conferenceHome = ConferenceHome(database)
    researchPaperHome = ResearchPaperHome(database)
    errorQueueHome = ErrorQueueHome(database)

    conferences = conferenceHome.get_conference()
    for c in conferences:
        conference = Conference(**c)
        # TODO do not get conference name from here
        log.info('Started processing: ' + conference.name)

        try:
            venues = get_venues_from_url(conference.dblp_url, conference.name, parser)
            log.debug("Fetched {} venues for conference {}".format(len(venues), conference.name))
            venueHome.store_many_venues(venues)

            proceedings = fetch_proceeding_info(conference.name, venues, parser, errorQueueHome)
            proceedingHome.store_many_proceedings(proceedings)
        except Exception as ex:
            errorQueueHome.store_error_queue_item(ErrorQueueItem(ErrorQueueItem.TYPE_VENUE, conference.dblp_url))
            log.error("Parsing error for venues of conference {}. Error: {}".format(conference.name, ex))
            pass

        # proceedings = proceedingHome.get_proceedings({"conference_name": conference.name})
        # for p in proceedings:
        #     proceeding = Proceeding(**p)
        #     log.info("Started processing for " + proceeding.title)
        #
        #     try:
        #         base_url = "https://dblp.org/search/publ/api?q=toc:"
        #         url = base_url + p['dblp_url'].split(".html")[0] + ".bht"
        #         url += ":&h=1000&format=json"
        #
        #         obj = get_research_papers_from_url(url)
        #         total = int(obj['result']['hits']['@total'])
        #         fetched = int(obj['result']['hits']['@sent'])
        #         items_to_fetch_at_one_time = 1000
        #
        #         while fetched < total:
        #             if 'result' in obj and 'hits' in obj['result'] and 'hit' in obj['result']['hits']:
        #                 result = obj['result']
        #                 hits = result['hits']
        #                 for research_paper in hits['hit']:
        #                     # TODO decode html entities from the strings
        #                     research_paper['_id'] = research_paper['info']['title']
        #                     research_paper['proceeding_dblp_url'] = p['dblp_url']
        #                     researchPaperHome.store_research_paper(research_paper)
        #
        #             toFetch = items_to_fetch_at_one_time if total - fetched > items_to_fetch_at_one_time else total - fetched
        #             url = base_url + p['dblp_url'].split(".html")[0] + ".bht"
        #             url += ":&h={}&f={}&format=json".format(toFetch, fetched)
        #             log.info("Additional research papers fetching from {}".format(url))
        #             obj = get_research_papers_from_url(url)
        #             fetched += toFetch
        #
        #     except Exception as ex:
        #         errorQueueHome.store_error_queue_item(ErrorQueueItem(ErrorQueueItem.TYPE_RESEARCH_PAPERS, url))
        #         log.error("Parsing error for research papers of proceeding {}".format(proceeding.proceeding_key))
        #         pass
        #
        # conferenceHome.delete_conference({"_id": conference.id})