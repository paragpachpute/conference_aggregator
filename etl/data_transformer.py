import json
import logging
import os
import re

from database.proceeding_home import ProceedingHome
from database.transformed_venue_home import TransformedVenueHome
from entity.proceeding import Proceeding

log = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

class DataTransformer:
    def __init__(self):
        self.count = 0
        self.total = 0
        self.months = ["January", "February", "March","April","May","June","July","August","September","October","November", "December"]

    def transform_proceeding(self, proceeding):
        try:
            if "workshop" in proceeding.title.lower():
                invitation_type = 'workshop'
            else:
                invitation_type = 'conference'

            series_name = "/".join(proceeding.proceeding_key.split("/")[1:-1])
            venue_type = proceeding.proceeding_key.split("/")[0]

            occurrence_instance = {}
            occurrence_instance["invitation_type"] = invitation_type + '_occurrence'
            occurrence_instance["title"] = proceeding.title
            occurrence_instance["location"] = proceeding.location
            occurrence_instance["year"] = proceeding.year
            occurrence_instance["parent"] = []
            occurrence_instance["parent"].append("/".join(proceeding.proceeding_key.split("/")[:-1]))
            occurrence_instance["program chairs"] = proceeding.editors
            occurrence_instance["publisher"] = proceeding.publisher
            occurrence_instance["external link"] = proceeding.ee
            occurrence_instance["book"] = proceeding.booktitle
            occurrence_instance["key"] = proceeding.proceeding_key
            occurrence_instance["dblp_url"] = proceeding.dblp_url
            occurrence_instance["conference_date"] = self.get_date_from_string(proceeding.title)
            occurrence_instance["_id"] = {"invitation_type": occurrence_instance["invitation_type"],
                                          "key": occurrence_instance["key"]}

            series_instance = {}
            series_instance["invitation_type"] = invitation_type + '_series'
            series_instance["name"] = proceeding.conference_name
            series_instance["key"] = "/".join(proceeding.proceeding_key.split("/")[:-1])
            series_instance["short_name"] = series_name.upper()
            series_instance["_id"] = {"invitation_type": series_instance["invitation_type"],
                                      "key": series_instance["key"]}

            if proceeding.parent_link is not None and "https://dblp.org/db/" in proceeding.parent_link:
                # Mapping 'https://dblp.org/db/conf/nips/index.html' => 'conf/nips/2017'
                parent = proceeding.parent_link.split("https://dblp.org/db/")[1]  # => conf/nips/index.html
                parent = "/".join(parent.split("/")[:-1])  # => conf/nips
                parent += "/" + proceeding.year  # => conf/nips/2017
                occurrence_instance["parent"].append(parent)

            if occurrence_instance["conference_date"] is None:
                print("yo")

            self.total += 1
            return occurrence_instance, series_instance

        except Exception as e:
            self.count += 1
            log.error(
                "Failed while doing proceeding transformation for {} with error: {}".format(proceeding.proceeding_key,
                                                                                            e))
            return None, None

    def get_date_from_string(self, string):
        for month in self.months:
            tokens = string.split(",")
            for t in range(len(tokens)):
                if month in tokens[t]:
                    date = tokens[t]
                    if t + 1 < len(tokens) and not re.match(".*([1-3][0-9]{3})", date):
                        if re.search("[1-3][0-9]{3}", tokens[t + 1]) is not None:
                            date += "," + re.search("[1-3][0-9]{3}", tokens[t + 1]).group(0)

                    return date.strip()

database_name = "test_database"
transformer = DataTransformer()
transformed_venue_home = TransformedVenueHome(database_name)
proceeding_home = ProceedingHome(database_name)
for p in proceeding_home.get_proceedings():
    proceeding = Proceeding(**p)
    occurrence, series = transformer.transform_proceeding(proceeding)
    transformed_venue_home.store_venue(occurrence)
    transformed_venue_home.store_venue(series)
    if 'akbc' in occurrence['key']:
        print(json.dumps(occurrence, indent=2))
        print(json.dumps(series, indent=2))
        print("yo")


print("count", transformer.count)
print("total", transformer.total)