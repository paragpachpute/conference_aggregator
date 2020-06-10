from .connection_utils import get_database

class ResearchPaperHome:

    def __init__(self, database_name):
        self.database_name = database_name

        research_paper_collection_name = 'research_paper'

        self.db = get_database(self.database_name)
        self.research_paper_collection = self.db[research_paper_collection_name]

    def store_many_research_papers(self, research_papers):
        for c in research_papers:
            self.store_research_paper(c)

    def store_research_paper(self, research_paper):
        criteria = {"_id": research_paper['_id']}
        self.research_paper_collection.replace_one(criteria, research_paper, upsert=True)

    def get_research_papers(self, criteria={}):
        return self.research_paper_collection.find(criteria)
