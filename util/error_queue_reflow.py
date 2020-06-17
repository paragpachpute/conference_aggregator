import logging
import os

from database.error_queue_home import ErrorQueueHome
from entity.error_queue_item import ErrorQueueItem
from etl.dblp_venue_runner import get_venues_from_url
from parser.dblp.venue_parser import VenueParser
from database.venue_home import VenueHome

log = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def reflow_venue_erros(error_queue_home, parser, venue_home):
    criteria = {"type": ErrorQueueItem.TYPE_VENUE}
    errors = error_queue_home.get_error_queue_item(criteria)
    for e in errors:
        error = ErrorQueueItem(**e)
        log.info("Started reflow for {}".format(error.url))
        venues = get_venues_from_url(error.url, "error_reflow", parser)
        # TODO ideally store should not be called here, it should be called from dblp_venue_runner.py itself
        venue_home.store_many_venues(venues)
        error_queue_home.delete_error_queue_item({"_id" : error._id})


error_queue_home = ErrorQueueHome()
parser = VenueParser()
venue_home = VenueHome()
reflow_venue_erros(error_queue_home, parser, venue_home)