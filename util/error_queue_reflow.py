import logging
import os

from database.error_queue_home import ErrorQueueHome
from entity.error_queue_item import ErrorQueueItem
from etl.dblp_venue_runner import get_venues_from_url
from parser.dblp.venue_parser import VenueParser
from database.venue_home import VenueHome
from database.proceeding_home import ProceedingHome
from etl.dblp_venue_runner import fetch_proceeding_info

log = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def reflow_venue_erros(error_queue_home, parser, venue_home, proceeding_home):
    conference_name = "error_reflow"
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



database = 'test_database'
error_queue_home = ErrorQueueHome(database)
parser = VenueParser()
venue_home = VenueHome(database)
proceeding_home = ProceedingHome(database)
reflow_venue_erros(error_queue_home, parser, venue_home, proceeding_home)