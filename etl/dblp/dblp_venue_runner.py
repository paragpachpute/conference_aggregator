import json
import logging
import os
import urllib.request
from urllib.error import HTTPError

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


def fetch_proceeding_info(conference_name, venues, parser, errorQueueHome=None):
    proceedings = []
    proceeding_xml_base_url = "https://dblp.org/rec/xml/"
    for venue in venues:
        for proceeding_id in venue.proceedings:
            try:
                url = proceeding_xml_base_url + proceeding_id + ".xml"
                log.debug("Fetching from proceeding url: {}".format(url))
                proceeding = get_proceeding_info_from_url(conference_name, url, parser)
                proceeding.parent_link = venue.dblp_link
                proceeding.location = venue.location
                proceedings.append(proceeding)
            except Exception as ex:
                # TODO store conference name as well here
                if errorQueueHome is not None:
                    errorQueueHome.store_error_queue_item(ErrorQueueItem(ErrorQueueItem.TYPE_PROCEEDING_INFO, url))
                log.error("Parsing error for proceeding_id {} of conference {}. Error: {}".format(proceeding_id,
                                                                                                  conference_name, ex))
                pass
    return proceedings


def get_proceeding_info_from_url(conference_name, url, parser):
    xml = urllib.request.urlopen(url)
    proceeding = parser.get_proceeding(conference_name, xml.read())
    return proceeding


def get_venues_from_url(url, parser):
    document = urllib.request.urlopen(url)
    conference_name, venues = parser.parse(document.read())
    return conference_name, venues


def get_research_papers_from_url(url, proceeding_key):
    try:
        research_papers = []
        json_doc = urllib.request.urlopen(url)
        obj = json.loads(json_doc.read())

        if 'result' in obj:
            if "Unknown Error" in obj["result"]["status"]["text"]:
                return

            if 'hits' in obj['result'] and 'hit' in obj['result']['hits']:
                total = int(obj['result']['hits']['@total'])
                fetched = int(obj['result']['hits']['@sent'])
                items_to_fetch_at_one_time = 1000

                while fetched <= total:
                    if 'hits' in obj['result'] and 'hit' in obj['result']['hits']:
                        result = obj['result']
                        hits = result['hits']
                        for research_paper in hits['hit']:
                            # TODO decode html entities from the strings
                            research_paper['_id'] = research_paper['info']['title']
                            research_paper['proceeding_key'] = proceeding_key
                            research_papers.append(research_paper)

                        toFetch = items_to_fetch_at_one_time if total - fetched > items_to_fetch_at_one_time else total - fetched
                        # base_url = "https://dblp.org/search/publ/api?q=toc:"
                        # url = base_url + p['dblp_url'].split(".html")[0] + ".bht"
                        if toFetch == 0:
                            break
                        new_url = url.split(".bht")[0]
                        new_url += ".bht:&h={}&f={}&format=json".format(toFetch, fetched)
                        log.info("Additional research papers fetching from {}".format(new_url))
                        json_doc = urllib.request.urlopen(new_url)
                        obj = json.loads(json_doc.read())
                        fetched += toFetch

        return research_papers
    except HTTPError as ex:
        if ex.code == 500:
            return []
        else:
            raise Exception(ex)


if __name__ == '__main__':
    database = 'dev'
    parser = VenueParser()
    venueHome = VenueHome(database)
    proceedingHome = ProceedingHome(database)
    conferenceHome = ConferenceHome(database)
    researchPaperHome = ResearchPaperHome(database)
    errorQueueHome = ErrorQueueHome(database)

    # criteria = {"dblp_url": "https://dblp.org/db/conf/3dic/"}
    conferences = conferenceHome.get_conference()
    for c in conferences:
        conference = Conference(**c)
        log.info('Started processing: ' + conference.dblp_url)

        try:
            conference_name, venues = get_venues_from_url(conference.dblp_url, parser)
            log.debug("Fetched {} venues for conference {}".format(len(venues), conference_name))
            venueHome.store_many_venues(venues)

            proceedings = fetch_proceeding_info(conference_name, venues, parser, errorQueueHome)
            proceedingHome.store_many_proceedings(proceedings)
        except Exception as ex:
            errorQueueHome.store_error_queue_item(ErrorQueueItem(ErrorQueueItem.TYPE_VENUE, conference.dblp_url))
            log.error("Parsing error for venues of conference {}. Error: {}".format(conference_name, ex))
            pass

        proceedings = proceedingHome.get_proceedings({"conference_name": conference_name})
        for p in proceedings:
            proceeding = Proceeding(**p)
            log.info("Started processing for " + proceeding.title)

            try:
                base_url = "https://dblp.org/search/publ/api?q=toc:"
                url = base_url + p['dblp_url'].split(".html")[0] + ".bht"
                url += ":&h=1000&format=json"

                research_papers = get_research_papers_from_url(url, proceeding.proceeding_key)
                researchPaperHome.store_many_research_papers(research_papers)
                research_paper_keys = []
                for paper in research_papers:
                    research_paper_keys.append(paper['info']['key'])
                proceeding.research_papers = research_paper_keys
                proceedingHome.store_proceeding(proceeding)

            except Exception as ex:
                errorQueueHome.store_error_queue_item(
                    ErrorQueueItem(ErrorQueueItem.TYPE_RESEARCH_PAPERS, url, proceeding.proceeding_key))
                log.error(
                    "Parsing error for research papers of proceeding {}. Error {}".format(proceeding.proceeding_key,
                                                                                          ex))

        conferenceHome.delete_conference({"_id": conference.id})
