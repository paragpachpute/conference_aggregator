from util.utils import auto_str


@auto_str
class Proceeding:
    def __init__(self, title, booktitle=None, publisher=None, series=None, volume=None, year=None, isbn=None,
                 ee=None, dblp_url=None, proceeding_key=None, mdate=None, editors=None, conference_name=None, _id=None):
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
        self._id = _id
