import logging
import os

from bs4 import BeautifulSoup

log = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class VenueListParser:
    def parse(self, document):
        venue_list = []
        soup = BeautifulSoup(document, features="html.parser")
        list_content_div = soup.find("div", {"class": "hide-body"})
        venues = list_content_div.find_all("li")
        for conf in venues:
            v = conf.a['href']
            venue_list.append(v)
        log.debug("Retrieved {} venues links".format(len(venue_list)))
        return venue_list
