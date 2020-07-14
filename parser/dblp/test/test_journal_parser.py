from unittest import TestCase

from parser.dblp.journal_parser import JournalParser


class TestJournalParser(TestCase):
    def setUp(self) -> None:
        self.journal_parser = JournalParser()

    def test_parse(self):
        with open('../resources/journals.json') as json_file:
            papers = self.journal_parser.parse(json_file.read())
            self.assertEqual(124, len(papers['hit']))
