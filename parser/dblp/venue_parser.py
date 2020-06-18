import logging
import os
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

from entity.proceeding import Proceeding
from entity.venue import Venue
from util.utils import verbose_print

log = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class VenueParser:
    def parse(self, conference_name, document):
        log.info("Started Parsing for " + conference_name)
        soup = BeautifulSoup(document, features="html.parser")
        h2s = soup.find_all('h2')
        venues = self.get_venues(conference_name, h2s)
        uls = soup.find_all("ul", {"class": "publ-list"})
        self.populate_venue_proceeding_ids(venues, uls)
        return venues

    def get_venues(self, conference_name, h2s):
        venues = []
        for h2 in h2s:
            year = h2['id'] if 'id' in h2 else None
            dblp_link = None
            if h2.find('a'):
                dblp_link = h2.a['href']
            title = h2.text
            location = h2.text.split(':')[1].strip() if ':' in h2.text else None
            venues.append(Venue(title, location, year, dblp_link, conference_name))

        verbose_print('Fetched ' + str(len(venues)) + ' venues')
        return venues

    def getTextIfPresent(self, elem, tag):
        val = elem.find(tag)
        if val is not None:
            return val.text
        return None

    def populate_venue_proceeding_ids(self, venues, uls):
        for i in range(len(uls)):
            ul = uls[i]
            proceeding_ids = []
            lis = ul.find_all('li', {"class": "entry editor toc"})
            for li in lis:
                proceeding_ids.append(li['id'])
            venues[i].proceedings = proceeding_ids

        verbose_print('Fetched proceeding ids for ' + str(len(uls)) + ' venues')

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
