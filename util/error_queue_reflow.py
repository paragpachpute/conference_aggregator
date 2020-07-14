import logging
import os

from database.error_queue_home import ErrorQueueHome
from database.proceeding_home import ProceedingHome
from database.research_paper_home import ResearchPaperHome
from database.venue_home import VenueHome
from etl.dblp.dblp_venue_runner import fetch_proceeding_info
from etl.dblp.dblp_venue_runner import get_research_papers_from_url
from etl.dblp.dblp_venue_runner import get_venues_from_url
from parser.dblp.paper_parser import PaperParser
from parser.dblp.venue_parser import VenueParser

log = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def reflow_venue_erros(error_queue_home, parser, venue_home, proceeding_home):
    criteria = {"type": ErrorQueueItem.TYPE_VENUE}
    errors = error_queue_home.get_error_queue_item(criteria)
    log.info("Found {} errors for type {}".format(errors.count(), ErrorQueueItem.TYPE_VENUE))
    for e in errors:
        error = ErrorQueueItem(**e)
        log.info("Started re-flow for {}".format(error.url))
        conference_name, venues = get_venues_from_url(error.url, parser)
        # TODO ideally store should not be called here, it should be called from dblp_venue_runner.py itself
        venue_home.store_many_venues(venues)
        error_queue_home.delete_error_queue_item({"_id" : error.id})

        proceedings = fetch_proceeding_info(conference_name, venues, parser)
        proceeding_home.store_many_proceedings(proceedings)

def reflow_research_paper_errors(error_queue_home, parser, research_paper_home):
    criteria = {"type": ErrorQueueItem.TYPE_RESEARCH_PAPERS}
    errors = error_queue_home.get_error_queue_item(criteria)
    log.info("Found {} errors for type {}".format(errors.count(), ErrorQueueItem.TYPE_VENUE))
    for e in errors:
        error = ErrorQueueItem(**e)
        log.info("Started re-flow for {}".format(error.url))
        # TODO ideally storing should also be done in dblp_venue_runner.py
        research_papers = get_research_papers_from_url(error.url, error.proceeding_key)
        research_paper_home.store_many_research_papers(research_papers)
        error_queue_home.delete_error_queue_item({"_id" : error.id})


database = 'test_database'
error_queue_home = ErrorQueueHome(database)

venue_parser = VenueParser()
venue_home = VenueHome(database)
proceeding_home = ProceedingHome(database)
# reflow_venue_erros(error_queue_home, venue_parser, venue_home, proceeding_home)

paper_parser = PaperParser()
research_paper_home = ResearchPaperHome(database)
reflow_research_paper_errors(error_queue_home, paper_parser, research_paper_home)