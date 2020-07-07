import logging
import os

from bs4 import BeautifulSoup

log = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class ConferenceListParser:
    def parse(self, document):
        conferences = []
        soup = BeautifulSoup(document, features="html.parser")
        list_content_div = soup.find("div", {"class": "hide-body"})
        confs = list_content_div.find_all("li")
        for conf in confs:
            c = conf.a['href']
            conferences.append(c)
        log.debug("Retrieved {} conference links".format(len(conferences)))
        return conferences
