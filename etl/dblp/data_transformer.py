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
                invitation_type = 'Workshop'
            else:
                invitation_type = 'Conference'

            series_name = "/".join(proceeding.proceeding_key.split("/")[1:-1])
            venue_type = proceeding.proceeding_key.split("/")[0]

            occurrence_instance = {}
            occurrence_instance["_id"] = self.get_id_from_key(proceeding.proceeding_key) + "/" + invitation_type
            occurrence_instance["invitations"] = "Venue/-/" + invitation_type + "/Occurrence"
            occurrence_instance["readers"] = ["everyone"]
            occurrence_instance["nonreaders"] = []
            occurrence_instance["writers"] = ["Venue"]
            occurrence_instance["content"] = {}

            occurrence_instance["content"]["name"] = proceeding.title.split(",")[0]
            occurrence_instance["content"]["location"] = proceeding.location
            occurrence_instance["content"]["year"] = proceeding.year
            occurrence_instance["content"]["parents"] = []
            occurrence_instance["content"]["parents"].append(self.get_parent_id_from_key(proceeding.proceeding_key) + "/" + invitation_type)
            occurrence_instance["content"]["program_chairs"] = proceeding.editors
            occurrence_instance["content"]["publisher"] = proceeding.publisher
            occurrence_instance["content"]["url"] = proceeding.ee
            occurrence_instance["content"]["shortname"] = proceeding.booktitle
            occurrence_instance["content"]["dblp_key"] = proceeding.proceeding_key
            occurrence_instance["content"]["dblp_url"] = proceeding.dblp_url
            occurrence_instance["content"]["conference_date"] = self.get_date_from_string(proceeding.title)


            series_instance = {}
            series_instance["_id"] = self.get_parent_id_from_key(proceeding.proceeding_key) + "/" + invitation_type

            series_instance["invitations"] = "Venue/-/" + invitation_type + "/Series"
            series_instance["readers"] = ["everyone"]
            series_instance["nonreaders"] = []
            series_instance["writers"] =  ["Venue"]
            series_instance["content"] =  {}

            series_instance["content"]["name"] = proceeding.conference_name
            series_instance["content"]["short_name"] = series_name.upper()

            if proceeding.parent_link is not None and "https://dblp.org/db/" in proceeding.parent_link:
                # Mapping 'https://dblp.org/db/conf/nips/index.html' => 'conf/nips/2017'
                parent = proceeding.parent_link.split("https://dblp.org/db/")[1]  # => conf/nips/index.html
                parent = "/".join(parent.split("/")[:-1])  # => conf/nips
                parent += "/" + proceeding.year  # => conf/nips/2017
                occurrence_instance["content"]["parents"].append(self.get_id_from_key(parent) + "/" + 'Conference')

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

    def get_id_from_key(self, key):
        """
        This function converts the DBLP key into OR specific id
        example: conf/akbc/2019 => .AKBC/2019
        :param key: String which should be converted
        :return: converted _id field as per OR's conventions
        """
        return "." + "/".join(key.split("/")[1:]).upper()

    def get_parent_id_from_key(self, key):
        """
        This function converts the DBLP key into OR specific id of the parent conference
        example: conf/akbc/2019 => .AKBC
        :param key: String which should be converted
        :return: converted parent _id field as per OR's conventions
        """
        return "." + "/".join(key.split("/")[1:-1]).upper()

database_name = "dev"
transformer = DataTransformer()
transformed_venue_home = TransformedVenueHome(database_name)
proceeding_home = ProceedingHome(database_name)
for p in proceeding_home.get_proceedings():
    proceeding = Proceeding(**p)
    occurrence, series = transformer.transform_proceeding(proceeding)
    # transformed_venue_home.store_venue(occurrence)
    # transformed_venue_home.store_venue(series)
    if 'akbc' in occurrence["content"]['dblp_key']:
        print(json.dumps(occurrence, indent=2))
        print(json.dumps(series, indent=2))
    # if 'hcomp' in occurrence['key']:
    #     print(json.dumps(occurrence, indent=2))
    #     print(json.dumps(series, indent=2))


print("count", transformer.count)
print("total", transformer.total)