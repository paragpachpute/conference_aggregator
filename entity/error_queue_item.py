class ErrorQueueItem:
    TYPE_PROCEEDING_INFO = 'proceeding_info'
    TYPE_VENUE = 'venue'
    TYPE_RESEARCH_PAPERS = 'research_papers'

    def __init__(self, type, url, _id=None):
        self.type = type
        self.url = url
        self._id = _id if _id is not None else url