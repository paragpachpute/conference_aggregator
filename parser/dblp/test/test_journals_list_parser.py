from unittest import TestCase

from parser.dblp.journals_list_parser import JournalListParser


class TestJournalsListParser(TestCase):
    def setUp(self) -> None:
        self.journals_list_parser = JournalListParser()

    def test_get_venues(self):
        with open('../resources/journals_list.htm') as document:
            journals_list = self.journals_list_parser.parse(document.read())
            self.assertEqual(100, len(journals_list))