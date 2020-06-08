from util.utils import verbose_print
from bs4 import BeautifulSoup
from entity.venue import Venue
from entity.proceeding import Proceeding
import xml.etree.ElementTree as ET


class VenueParser:
    def parse(self, document):
        verbose_print('Started Parsing')
        soup = BeautifulSoup(document, features="html.parser")

        h2s = soup.find_all('h2')
        venues = self.get_venues(h2s)

        uls = soup.find_all("ul", {"class": "publ-list"})
        self.populate_venue_proceeding_ids(venues, uls)

        self.fetch_proceeding_info(venues)
        print(venues)

        return venues

    def get_venues(self, h2s):
        venues = []
        for h2 in h2s:
            try:
                year = h2['id']
                dblp_link = None
                if h2.find('a'):
                    dblp_link = h2.a['href']
                title = h2.text
                location = h2.text.split(':')[1]
                venues.append(Venue(title, location, year, dblp_link))
            except Exception as e:
                # TODO add logic for adding the venue into parsing error table
                print(h2)

        verbose_print('Fetched ' + str(len(venues)) + ' venues')
        return venues

    def getTextIfPresent(self, elem, tag):
        val = elem.find(tag)
        if val is not None:
            return val.text
        return None

    def populate_venue_proceeding_ids(self, venues, uls):
        # TODO add exception handling logic
        for i in range(len(uls)):
            ul = uls[i]
            proceeding_ids = []
            lis = ul.find_all('li', {"class": "entry editor toc"})
            for li in lis:
                proceeding_ids.append(li['id'])
            venues[i].proceedings = proceeding_ids

        verbose_print('Fetched proceeding ids for ' + str(len(uls)) + ' venues')

    def fetch_proceeding_info(self, venues):
        proceeding_xml_base_url = "https://dblp.org/rec/xml/"
        for venue in venues:
            for proceeding_id in venue.proceedings:
                url = proceeding_xml_base_url + proceeding_id
                # TODO make HTTP request and get the XML
                response = None
                # proceeding = self.get_proceeding(response)
                # TODO store proceeding into the database

    def get_proceeding(self, xml):
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

        return proceeding