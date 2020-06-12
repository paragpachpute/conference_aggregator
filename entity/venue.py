from util.utils import auto_str

@auto_str
class Venue:
    def __init__(self, title, location, year, dblp_link, conference_name, proceedings=None, _id=None):
        self.title = title
        self.location = location
        self.year = year
        self.dblp_link = dblp_link
        self.proceedings = proceedings if proceedings is not None else []
        self.conference_name = conference_name
        self._id = _id if _id is not None else title
