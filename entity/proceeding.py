from util.utils import auto_str

@auto_str
class Proceeding:
    def __init__(self, title):
        self.title = None
        self.booktitle = None
        self.publisher = None
        self.series = None
        self.volume = None
        self.year = None
        self.isbn = None
        self.ee = None
        self.dblp_url = None
        self.proceeding_key = None
        self.mdate = None
        self.editors = None
        self._id = title
        self.conference_name = None