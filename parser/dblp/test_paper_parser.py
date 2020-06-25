from unittest import TestCase
from parser.dblp.paper_parser import PaperParser

class TestPaperParser(TestCase):
    def setUp(self) -> None:
        self.paper_parser = PaperParser()

    def test_parse(self):
        with open('proceeding_papers.json') as json_file:
            papers = self.paper_parser.parse(json_file.read())
            self.assertEqual(25, len(papers['hit']))