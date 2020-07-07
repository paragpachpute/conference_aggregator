import logging
import os
import urllib.request

from parser.dblp.conference_list_parser import ConferenceListParser

log = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def get_conferences_list_from_url(url, parser):
    doc = urllib.request.urlopen(url)
    return parser.parse(doc.read())


if __name__ == '__main__':
    total_venue_pages = 110
    parser = ConferenceListParser()
    base_url = "https://dblp.org/db/conf/"

    all_confs = []
    errors = []
    total_links_retrieved = 0

    for i in range(total_venue_pages):
        url = base_url + "?pos={}".format(i * 100)
        try:
            conf_list = get_conferences_list_from_url(url, parser)
            if len(conf_list) == 0:
                break
            all_confs.extend(conf_list)
            total_links_retrieved += len(conf_list)
            log.info("Retrieved {} conference links".format(total_links_retrieved))
        except Exception as ex:
            log.error("Parsing error for conference list with url {}. Exception: {}".format(url, ex))
            errors.append(url)

    log.info("Venue links fetching complete. Fetched {} unique links, found {} errors".format(len(set(all_confs)),
                                                                                             len(set(errors))))
    with open("output/conference_list.txt", "w") as f:
        for venue in set(all_confs):
            f.write(venue + "\n")

    if len(errors) > 0:
        with open("output/errors_conference_list.txt", "w") as f:
            for error in set(errors):
                f.write(error + "\n")
