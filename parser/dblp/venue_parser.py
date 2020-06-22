import logging
import os
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

from entity.proceeding import Proceeding
from entity.venue import Venue

log = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class VenueParser:
    def parse(self, conference_name, document):
        log.info("Started Parsing for " + conference_name)
        soup = BeautifulSoup(document, features="html.parser")
        venues = []
        h2 = soup.find("h2")
        if h2 is not None:
            venues.append(self.get_venue(conference_name, h2))

            elem = h2.find_next(["h2", "li"])
            while elem is not None:
                if elem.name == "h2":
                    venues.append(self.get_venue(conference_name, elem))
                if elem.name == "li" and elem.get("class") == "entry editor toc".split():
                    li = elem
                    venues[len(venues)-1].proceedings.append(li["id"])
                elem = elem.find_next(["h2", "li"])

            log.info("Fetched {} venues for conference {}".format(len(venues), conference_name))
        return venues


    def get_venue(self, conference_name, h2):
        year = h2['id'] if 'id' in h2 else None
        dblp_link = None
        if h2.find('a'):
            dblp_link = h2.a['href']
        title = h2.text
        location = h2.text.split(':')[1].strip() if ':' in h2.text else None
        return Venue(title, location, year, dblp_link, conference_name)

    def getTextIfPresent(self, elem, tag):
        val = elem.find(tag)
        if val is not None:
            return val.text
        return None

    # def populate_venue_proceeding_ids(self, venues, uls):
    #     for i in range(len(uls)):
    #         ul = uls[i]
    #         proceeding_ids = []
    #         lis = ul.find_all('li', {"class": "entry editor toc"})
    #         for li in lis:
    #             proceeding_ids.append(li['id'])
    #         venues[i].proceedings = proceeding_ids
    #
    #     verbose_print('Fetched proceeding ids for ' + str(len(uls)) + ' venues')

    def get_proceeding(self, conference_name, xml):
        root = ET.fromstring(xml)
        proceeding_tag = root[0]
        title = self.getTextIfPresent(proceeding_tag, 'title')
        proceeding = Proceeding(title)
        proceeding.proceeding_key = proceeding_tag.get('key')
        proceeding.mdate = proceeding_tag.get('mdate')
        editors = proceeding_tag.findall('editor')
        proceeding.editors = [e.text for e in editors] if editors is not None else []
        proceeding.booktitle = self.getTextIfPresent(proceeding_tag, 'booktitle')
        proceeding.publisher = self.getTextIfPresent(proceeding_tag, 'publisher')
        proceeding.series = self.getTextIfPresent(proceeding_tag, 'series')
        proceeding.volume = self.getTextIfPresent(proceeding_tag, 'volume')
        proceeding.year = self.getTextIfPresent(proceeding_tag, 'year')
        proceeding.isbn = self.getTextIfPresent(proceeding_tag, 'isbn')
        proceeding.ee = self.getTextIfPresent(proceeding_tag, 'ee')
        proceeding.dblp_url = self.getTextIfPresent(proceeding_tag, 'url')
        proceeding.conference_name = conference_name

        return proceeding
