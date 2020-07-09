import logging
import os

from bs4 import BeautifulSoup

log = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class JournalListParser:
    def parse(self, document):
        journals_list = []
        soup = BeautifulSoup(document, features="html.parser")
        list_content_div = soup.find("div", {"class": "hide-body"})
        venues = list_content_div.find_all("li")
        for conf in venues:
            v = conf.a['href']
            journals_list.append(v)
        log.debug("Retrieved {} journal links".format(len(journals_list)))
        return journals_list
