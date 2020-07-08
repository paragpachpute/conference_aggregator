import logging
import os
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

from entity.proceeding import Proceeding
from entity.venue import Venue

log = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class VenueParser:
    """
    Naming convention:
    venue: It represents a conference instance. ex: NIPS/2017
    proceeding: It represents different events in that instance like workshops, conferences. ex: ViGIL, ML4H, etc.
    """

    def parse(self, document):
        soup = BeautifulSoup(document, features="html.parser")
        venues = []
        conference_name = soup.find("h1").text
        h2 = soup.find("h2")
        if h2 is not None:
            venues.append(self.get_venue(conference_name, h2))
            # Find next h2 or li element. h2 contains venue information while li contains proceedings information
            elem = h2.find_next(["h2", "li"])
            while elem is not None:
                if elem.name == "h2":
                    venues.append(self.get_venue(conference_name, elem))
                if elem.name == "li" and elem.get("class") == "entry editor toc".split():
                    li = elem
                    venues[len(venues) - 1].proceedings.append(li["id"])
                elem = elem.find_next(["h2", "li"])
        return conference_name, venues

    def get_venue(self, conference_name, h2):
        year = h2['id'] if 'id' in h2 else None
        dblp_link = None
        if h2.find('a'):
            dblp_link = h2.a['href']
        title = h2.text
        location = h2.text.split(':')[1].strip() if ':' in h2.text else None
        return Venue(title, location, year, dblp_link, conference_name)

    def get_text_if_present(self, elem, tag):
        val = elem.find(tag)
        if val is not None:
            return val.text
        return None

    def get_proceeding(self, conference_name, xml):
        root = ET.fromstring(xml)
        proceeding_tag = root[0]
        title = self.get_text_if_present(proceeding_tag, 'title')
        proceeding = Proceeding(title)
        proceeding.proceeding_key = proceeding_tag.get('key')
        proceeding.mdate = proceeding_tag.get('mdate')
        editors = proceeding_tag.findall('editor')
        proceeding.editors = [e.text for e in editors] if editors is not None else []
        proceeding.booktitle = self.get_text_if_present(proceeding_tag, 'booktitle')
        proceeding.publisher = self.get_text_if_present(proceeding_tag, 'publisher')
        proceeding.series = self.get_text_if_present(proceeding_tag, 'series')
        proceeding.volume = self.get_text_if_present(proceeding_tag, 'volume')
        proceeding.year = self.get_text_if_present(proceeding_tag, 'year')
        proceeding.isbn = self.get_text_if_present(proceeding_tag, 'isbn')
        proceeding.ee = self.get_text_if_present(proceeding_tag, 'ee')
        proceeding.dblp_url = self.get_text_if_present(proceeding_tag, 'url')
        proceeding.conference_name = conference_name
        return proceeding
