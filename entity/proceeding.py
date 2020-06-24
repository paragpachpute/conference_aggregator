from util.utils import auto_str


@auto_str
class Proceeding:
    def __init__(self, title, booktitle=None, publisher=None, series=None, volume=None, year=None, isbn=None,
                 ee=None, dblp_url=None, proceeding_key=None, mdate=None, editors=None, conference_name=None,
                 parent_link=None, location=None, _id=None):
        self.title = title
        self.booktitle = booktitle
        self.publisher = publisher
        self.series = series
        self.volume = volume
        self.year = year
        self.isbn = isbn
        self.ee = ee
        self.dblp_url = dblp_url
        self.proceeding_key = proceeding_key
        self.mdate = mdate
        self.editors = editors
        self.conference_name = conference_name
        self.parent_link = parent_link
        self.location = location
        self._id = _id if _id is not None else title
