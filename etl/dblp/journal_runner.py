import concurrent
import itertools
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from logging import Formatter, StreamHandler
from random import random

from database.research_paper_home import ResearchPaperHome
from etl.dblp.dblp_venue_runner import get_research_papers_from_url

log = logging.getLogger()
log.setLevel(logging.getLevelName('INFO'))

log_formatter = Formatter("%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s")
console_handler = StreamHandler()
console_handler.setFormatter(log_formatter)
if len(log.handlers) == 0:
    log.addHandler(console_handler)
else:
    log.handlers[0].setFormatter(log_formatter)

def get_journal_url_from_name(journal_name):
    base_url = "https://dblp.org/search/publ/api?q=stream:streams/journals/"
    journal_url = base_url + journal_name + ":&h=1000&format=json"
    return journal_url

# url = "https://dblp.org/search/publ/api?q=stream%3Astreams%2Fjournals%2Fbdcc%3A&h=1000&format=json"
# papers = get_research_papers_from_url(url, None)
# print(len(url))

if __name__ == '__main__':
    database = 'test_database'
    researchPaperHome = ResearchPaperHome(database)

    journals_list = []
    already_fetched_list = []
    map_future_to_journal_name = {}
    with open("output/journals_list.txt", "r") as f:
        journal_name = f.readline().strip()
        while journal_name is not None and journal_name is not "":
            journals_list.append(journal_name)
            journal_name = f.readline().strip()

    journals_list = list(journals_list)
    log.info("Number of journals to fetch: {}".format(len(journals_list)))

    NUM_TASKS_AT_ONCE = 5
    with ThreadPoolExecutor(max_workers=NUM_TASKS_AT_ONCE) as executor:
        # Schedule the first N futures.  We don't want to schedule them all
        # at once, to avoid consuming excessive amounts of memory.
        futures = {
            executor.submit(get_research_papers_from_url, get_journal_url_from_name(journal_name), "journals/"+journal_name)
            for journal_name in itertools.islice(journals_list, NUM_TASKS_AT_ONCE)
        }
        while futures:
            # Wait for the next future to complete.
            done, futures = concurrent.futures.wait(
                futures, return_when=concurrent.futures.FIRST_COMPLETED
            )
            for future_journal_papers in done:
                try:
                    papers = future_journal_papers.result()
                    log.info("Fetched {} papers".format(len(papers)))
                    researchPaperHome.store_many_research_papers(papers)
                    # TODO make an API call to store the research paper

                except Exception as ex:
                    if future_journal_papers in map_future_to_journal_name:
                        journal_name = map_future_to_journal_name[future_journal_papers]
                        log.error(
                            "Parsing error for research papers of journal {} . Error {}".format(journal_name, ex))
                        with open("output/errors_journal_papers.txt", "a") as error_file:
                            error_file.write(journal_name + "\n")

            # Sleeping for a random time from [0,5) seconds so as to avoid "429: Too many requests" error
            time.sleep(5 * random())

            # Schedule the next set of futures.  We don't want more than N futures
            # in the pool at a time, to keep memory consumption down.
            for journal_name in itertools.islice(journals_list, len(done)):
                proceeding_key = "journals/"+journal_name
                f = executor.submit(get_research_papers_from_url, get_journal_url_from_name(journal_name), proceeding_key)
                map_future_to_journal_name[f] = journal_name
                futures.add(f)
            journals_list = journals_list[len(done):]
