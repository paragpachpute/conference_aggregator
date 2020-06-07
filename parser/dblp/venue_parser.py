from util.utils import verbose_print
from bs4 import BeautifulSoup
from entity.venue import Venue

class VenueParser:
    def parse(self, document):
        verbose_print('Started Parsing')
        soup = BeautifulSoup(document, features="html.parser")

        h2s = soup.find_all('h2')
        venues = self.get_venues(h2s)

    def get_venues(self, h2s):
        venues = []
        for h2 in h2s:
            try:
                year = h2['id']
                dblp_link = h2.a['href'] if 'a' in h2 else None
                title = h2.text
                location = h2.text.split(':')[1]
                venues.append(Venue(title, location, year, dblp_link))
            except Exception as e:
                # add logic for adding the venue into parsing error table
                print(h2)

        verbose_print('Fetched ' + str(len(venues)) + ' venues')
        return venues

with open('dblp_aaai.htm') as document:
    parser = VenueParser()
    obj = parser.parse(document)