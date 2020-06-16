from util.utils import auto_str


@auto_str
class Conference:
    def __init__(self, name, dblp_url, _id=None):
        self.name = name
        self.dblp_url = dblp_url
        self._id = _id if _id is not None else dblp_url