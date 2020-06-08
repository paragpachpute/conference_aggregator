from util.utils import auto_str

@auto_str
class Venue:
    def __init__(self, title, location, year, dblp_link):
        self.title = title
        self.location = location
        self.year = year
        self.dblp_link = dblp_link
        self.proceedings = []