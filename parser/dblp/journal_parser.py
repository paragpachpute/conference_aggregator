import json


class JournalParser:
    def __init__(self):
        pass

    def parse(self, json_doc):
        obj = json.loads(json_doc)
        result = obj['result']
        hits = result['hits']
        return hits
