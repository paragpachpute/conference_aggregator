import logging
import os
import urllib.request

from parser.dblp.journals_list_parser import JournalListParser

log = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def get_conferences_list_from_url(url, parser):
    doc = urllib.request.urlopen(url)
    return parser.parse(doc.read())


if __name__ == '__main__':
    total_journal_pages = 40
    parser = JournalListParser()
    base_url = "https://dblp.org/db/journals/"

    all_journals = []
    errors = []
    total_links_retrieved = 0

    for i in range(total_journal_pages):
        url = base_url + "?pos={}".format(i * 100)
        try:
            journals_list = get_conferences_list_from_url(url, parser)
            if len(journals_list) == 0:
                break
            all_journals.extend(journals_list)
            total_links_retrieved += len(journals_list)
            log.info("Retrieved {} journal links".format(total_links_retrieved))
        except Exception as ex:
            log.error("Parsing error for journal list with url {}. Exception: {}".format(url, ex))
            errors.append(url)

    log.info("Journal links fetching complete. Fetched {} unique links, found {} errors".format(len(set(all_journals)),
                                                                                                len(set(errors))))
    with open("output/journals_list.txt", "w") as f:
        for venue in set(all_journals):
            f.write(venue + "\n")

    if len(errors) > 0:
        with open("output/errors_journals_list.txt", "w") as f:
            for error in set(errors):
                f.write(error + "\n")
