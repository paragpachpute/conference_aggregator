import concurrent
import itertools
import json
import logging
import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from logging import Formatter, StreamHandler
from random import random
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
        for i in range(len(venue.proceedings)):
            proceeding_id = venue.proceedings[i]
            url = proceeding_xml_base_url + proceeding_id + ".xml"
            log.debug("Fetching from proceeding url: {}".format(url))
            proceeding = get_proceeding_info_from_url(conference_name, url, parser)
            proceeding.parent_link = venue.dblp_link
            proceeding.location = venue.location
            proceeding.editors_with_links = venue.proceeding_authors[i]
            proceedings.append(proceeding)

    return proceedings


def get_proceeding_info_from_url(conference_name, url, parser):
    xml = urllib.request.urlopen(url)
    proceeding = parser.get_proceeding(conference_name, xml.read())
    return proceeding


def get_venues_from_url(url, parser):
    document = urllib.request.urlopen(url)
    conference, venues = parser.parse(document.read())
    return conference, venues


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
                            # Need something to tie research paper back to its venue / journal
                            research_paper['proceeding_key'] = proceeding_key
                            research_papers.append(research_paper)

                        toFetch = items_to_fetch_at_one_time if total - fetched > items_to_fetch_at_one_time else total - fetched

                        if toFetch == 0:
                            break

                        new_url = url.split("&h=")[0]
                        new_url += "&h={}&f={}&format=json".format(toFetch, fetched)
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
        conference, venues = get_venues_from_url(venue_dblp_url, parser)
        conf_obj = {"invitation": "Venue/-/Conference", 'readers': ['everyone'], 'writers': ['Venue'],
                     "content": {
                         "dblp": vars(conference)
                     }
                     }
        posted_conf = client.post_venue(conf_obj)
        log.debug("Fetched {} venues for conference {}".format(len(venues), conference.name))
        venueHome.store_many_venues(venues)

        proceedings = fetch_proceeding_info(conference.name, venues, parser)
        proceedingHome.store_many_proceedings(proceedings)

        for proceeding in proceedings:
            # occurrence_instance, series_instance = data_transformer.transform_proceeding(proceeding)
            # transformed_venue_home.store_venue(occurrence_instance)
            # transformed_venue_home.store_venue(series_instance)
            raw_venue = {"invitation": "Venue/-/Conference/Occurrence", 'readers': ['everyone'], 'writers': ['Venue'],
                         "content": {
                             "dblp": vars(proceeding)
                         }
                         }
            posted_venue = client.post_venue(raw_venue)
            # print(json.dumps(posted_venue, indent=2))
            # client.post_venue(series_instance)
        with open("output/success_list.txt", "a") as f:
            f.write(venue_dblp_url + "\n")
            f.flush()

    except Exception as ex:
        if isinstance(ex, HTTPError) and ex.code == 429:
            retry_time = int(ex.headers.get('Retry-After'))
            log.info("Sleeping for {} seconds as server responded with 429".format(retry_time))
            time.sleep(retry_time)
            fetch_and_store_venue(venue_dblp_url, parser, client, venueHome, proceedingHome, transformed_venue_home,
                                  researchPaperHome)
        else:
            # print(vars(raw_venue))
            # occurrence_instance, series_instance = data_transformer.transform_proceeding(proceeding)
            log.error("Parsing error for venue {}. Error: {}".format(venue_dblp_url, ex))
            with open("output/errors_venue_info_retry.txt", "a") as error_file:
                error_file.write(venue_dblp_url + "\n")
            proceedings = []

    # for proceeding in proceedings:
    #     log.info("Started processing for " + proceeding.title)
    #
    #     try:
    #         base_url = "https://dblp.org/search/publ/api?q=toc:"
    #         url = base_url + proceeding.dblp_url.split(".html")[0] + ".bht"
    #         url += ":&h=1000&format=json"
    #
    #         research_papers = get_research_papers_from_url(url, proceeding.proceeding_key)
    #         researchPaperHome.store_many_research_papers(research_papers)
    #         # TODO make an API call to store the research paper
    #
    #     except Exception as ex:
    #         log.error(
    #             "Parsing error for research papers of proceeding {}. Error {}".format(proceeding.proceeding_key,
    #                                                                                   ex))
    #         with open("output/errors_research_paper.txt", "a") as error_file:
    #             error_file.write(proceeding.proceeding_key + "\n")


if __name__ == '__main__':
    database = 'test_database'
    parser = VenueParser()
    venueHome = VenueHome(database)
    proceedingHome = ProceedingHome(database)
    researchPaperHome = ResearchPaperHome(database)
    data_transformer = DataTransformer()
    transformed_venue_home = TransformedVenueHome(database)
    baseUrl = 'https://devapi.openreview.net'
    password = 'OpenReview_dev'
    # baseUrl = "http://localhost:3000"
    # password = '1234'
    client = openreview.Client(baseurl=baseUrl, username='OpenReview.net',
                               password=password)

    conf_list = []
    already_fetched_list = []
    with open("output/conference_list.txt", "r") as f:
        venue_dblp_url = f.readline().strip()
        while venue_dblp_url is not None and venue_dblp_url is not "":
            conf_list.append(venue_dblp_url)
            venue_dblp_url = f.readline().strip()

    if os.path.exists("output/success_list.txt"):
        with open("output/success_list.txt", "r") as f:
            venue_dblp_url = f.readline().strip()
            while venue_dblp_url is not None and venue_dblp_url is not "":
                already_fetched_list.append(venue_dblp_url)
                venue_dblp_url = f.readline().strip()

        conf_list = set(conf_list).difference(set(already_fetched_list))
    conf_list = list(conf_list)
    log.info("Number of conferences to fetch: {}".format(len(conf_list)))

    NUM_TASKS_AT_ONCE = 5
    with ThreadPoolExecutor(max_workers=NUM_TASKS_AT_ONCE) as executor:
        # Schedule the first N futures.  We don't want to schedule them all
        # at once, to avoid consuming excessive amounts of memory.
        futures = {
            executor.submit(fetch_and_store_venue, venue_dblp_url, parser, client, venueHome, proceedingHome,
                            transformed_venue_home,
                            researchPaperHome)
            for venue_dblp_url in itertools.islice(conf_list, NUM_TASKS_AT_ONCE)
        }
        while futures:
            # Wait for the next future to complete.
            done, futures = concurrent.futures.wait(
                futures, return_when=concurrent.futures.FIRST_COMPLETED
            )
            # Sleeping for a random time from [0,5) seconds so as to avoid "429: Too many requests" error
            time.sleep(20 * random())

            # Schedule the next set of futures.  We don't want more than N futures
            # in the pool at a time, to keep memory consumption down.
            for venue_dblp_url in itertools.islice(conf_list, len(done)):
                futures.add(
                    executor.submit(fetch_and_store_venue, venue_dblp_url, parser, client, venueHome, proceedingHome,
                                    transformed_venue_home,
                                    researchPaperHome)
                )
            conf_list = conf_list[len(done):]
