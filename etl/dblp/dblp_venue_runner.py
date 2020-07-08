import json
import logging
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from logging import Formatter, StreamHandler
from urllib.error import HTTPError

import openreview

from database.proceeding_home import ProceedingHome
from database.research_paper_home import ResearchPaperHome
from database.transformed_venue_home import TransformedVenueHome
from database.venue_home import VenueHome
from etl.dblp.data_transformer import DataTransformer
from parser.dblp.venue_parser import VenueParser

log = logging.getLogger()
log.setLevel(logging.getLevelName('INFO'))

log_formatter = Formatter("%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s")
console_handler = StreamHandler()
console_handler.setFormatter(log_formatter)
log.handlers[0].setFormatter(log_formatter)


def fetch_proceeding_info(conference_name, venues, parser):
    proceedings = []
    proceeding_xml_base_url = "https://dblp.org/rec/xml/"
    for venue in venues:
        for proceeding_id in venue.proceedings:
            url = proceeding_xml_base_url + proceeding_id + ".xml"
            log.debug("Fetching from proceeding url: {}".format(url))
            proceeding = get_proceeding_info_from_url(conference_name, url, parser)
            proceeding.parent_link = venue.dblp_link
            proceeding.location = venue.location
            proceedings.append(proceeding)

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
                            research_paper['_id'] = research_paper['info']['title']
                            research_paper['proceeding_key'] = proceeding_key
                            research_papers.append(research_paper)

                        toFetch = items_to_fetch_at_one_time if total - fetched > items_to_fetch_at_one_time else total - fetched

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


def fetch_and_store_venue(venue_dblp_url, parser, client, venueHome, proceedingHome, transformed_venue_home,
                          researchPaperHome):
    log.info('Started processing: ' + venue_dblp_url)
    try:
        conference_name, venues = get_venues_from_url(venue_dblp_url, parser)
        log.debug("Fetched {} venues for conference {}".format(len(venues), conference_name))
        venueHome.store_many_venues(venues)

        proceedings = fetch_proceeding_info(conference_name, venues, parser)
        proceedingHome.store_many_proceedings(proceedings)

        for proceeding in proceedings:
            occurrence_instance, series_instance = data_transformer.transform_proceeding(proceeding)
            transformed_venue_home.store_venue(occurrence_instance)
            transformed_venue_home.store_venue(series_instance)
            client.post_venue(occurrence_instance)
            client.post_venue(series_instance)

    except Exception as ex:
        log.error("Parsing error for venues of conference {}. Error: {}".format(conference_name, ex))
        with open("output/errors_venue_info.txt", "a") as error_file:
            error_file.write(venue_dblp_url + "\n")
        proceedings = []

    for proceeding in proceedings:
        log.info("Started processing for " + proceeding.title)

        try:
            base_url = "https://dblp.org/search/publ/api?q=toc:"
            url = base_url + proceeding.dblp_url.split(".html")[0] + ".bht"
            url += ":&h=1000&format=json"

            research_papers = get_research_papers_from_url(url, proceeding.proceeding_key)
            researchPaperHome.store_many_research_papers(research_papers)
            # TODO make an API call to store the research paper

        except Exception as ex:
            log.error(
                "Parsing error for research papers of proceeding {}. Error {}".format(proceeding.proceeding_key,
                                                                                      ex))
            with open("output/errors_research_paper.txt", "a") as error_file:
                error_file.write(proceeding.proceeding_key + "\n")


if __name__ == '__main__':
    database = 'test_database'
    parser = VenueParser()
    venueHome = VenueHome(database)
    proceedingHome = ProceedingHome(database)
    researchPaperHome = ResearchPaperHome(database)
    data_transformer = DataTransformer()
    transformed_venue_home = TransformedVenueHome(database)
    client = openreview.Client(baseurl='https://dev.openreview.net', username='OpenReview.net',
                               password='OpenReview_dev')

    with open("output/conference_list.txt", "r") as f:
        with ThreadPoolExecutor(max_workers=5) as executor:
            venue_dblp_url = f.readline().strip()
            while venue_dblp_url is not None:
                executor.submit(fetch_and_store_venue, venue_dblp_url, parser, client, venueHome, proceedingHome,
                                transformed_venue_home,
                                researchPaperHome)
                venue_dblp_url = f.readline().strip()
