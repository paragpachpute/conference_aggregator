class Conference:
    def __init__(self, name, dblp_url, home_url=None, _id=None):
        self.name = name
        self.dblp_url = dblp_url
        self.home_url = home_url
        self._id = _id if _id is not None else name