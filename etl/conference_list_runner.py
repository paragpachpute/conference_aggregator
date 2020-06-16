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
from parser.dblp.conference_list_parser import ConferenceListParser

log = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def get_conferences_list_from_url(url, parser):
    doc = urllib.request.urlopen(url)
    return parser.parse(doc.read())


if __name__ == '__main__':
    database = 'test_database'
    conferenceHome = ConferenceHome(database)
    errorQueueHome = ErrorQueueHome(database)
    parser = ConferenceListParser()

    base_url = "https://dblp.org/db/conf/"
    total_links_retrieved = 0
    for i in range(100):
        url = base_url + "?pos={}".format(i*100)
        try:
            conf_list = get_conferences_list_from_url(url, parser)
            conferenceHome.store_many_conference(conf_list)
            total_links_retrieved += len(conf_list)
            log.info("Retrieved {} conference links".format(total_links_retrieved))
        except Exception as ex:
            errorQueueHome.store_error_queue_item(ErrorQueueItem(ErrorQueueItem.TYPE_CONFERENCE_LIST, url))
            log.error("Parsing error for conference list with url {}. Exception: {}".format(url, ex))
