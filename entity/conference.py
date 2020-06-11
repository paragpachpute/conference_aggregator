class Conference:
    def __init__(self, name, dblp_url, home_url=None):
        self._id = name
        self.name = name
        self.dblp_url = dblp_url
        self.home_url = home_url