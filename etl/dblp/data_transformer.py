import datetime
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
        self.start_date_mismatch = 0
        self.end_date_mismatch = 0
        self.exceptions = 0
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
            conf_date_str = self.get_date_from_string(proceeding.title, proceeding.year)
            start = None
            end = None
            if conf_date_str is not None:
                start, end = self.get_timestamps_from_date_string(conf_date_str)
            occurrence_instance["content"]["start_date"] = start
            occurrence_instance["content"]["end_date"] = end


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
            conf_date_str = self.get_date_from_string(proceeding.title, proceeding.year)
            if conf_date_str is not None:
                start, end = self.get_timestamps_from_date_string(conf_date_str)

            log.error(
                "Failed while doing proceeding transformation for {} with error: {}".format(proceeding.proceeding_key,
                                                                                            e))
            return None, None

    def get_date_from_string(self, title_string, year):
        for month in self.months:
            tokens = title_string.split(",")
            for t in range(len(tokens)):
                if month in tokens[t]:
                    date = tokens[t]
                    if t + 1 < len(tokens) and not re.match(".*([1-3][0-9]{3})", date):
                        if re.search("[1-3][0-9]{3}", tokens[t + 1]) is not None:
                            date += "," + re.search("[1-3][0-9]{3}", tokens[t + 1]).group(0)

                    if not re.match(".*([1-3][0-9]{3})", date):
                        # year is not present in the date, add it manually
                        date += "," + year
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

    def get_timestamps_from_date_string(self, date_str):
        """
        Given string of the form 'March 13-17,2010' get start and end timestamps
        :param date_str: String representing the date range
        :return: start and end timestamps
        """
        start_timestamp = None
        end_timestamp = None

        for i in range(len(self.months)):
            if self.months[i] in date_str:
                year = re.search("[1-3][0-9]{3}", date_str).group(0)
                date_str = date_str.replace(year, '')
                if '-' in date_str:
                    if re.match(".*[1-9][0-9]?", date_str.split("-")[0]):
                        start_day = re.findall("[1-9][0-9]?", date_str.split("-")[0])[-1]
                    else:
                        self.start_date_mismatch += 1
                        start_day = 1
                    if re.match(".*[1-9][0-9]?", date_str.split("-")[1]):
                        end_day = re.findall("[1-9][0-9]?", date_str.split("-")[1])[0]
                    else:
                        self.end_date_mismatch +=1
                        end_day = start_day
                    start_timestamp = datetime.datetime(year=int(year), month=i+1, day=int(start_day))

                    try:
                        end_timestamp = datetime.datetime(year=int(year), month=i+1, day=int(end_day))
                    except Exception as e:
                        self.exceptions += 1
                        end_timestamp = start_timestamp

                else:
                    if re.match("[1-9][0-9]?", date_str):
                        start_day = re.findall("[1-9][0-9]?", date_str)[-1]
                        start_timestamp = datetime.datetime(year=int(year), month=i+1, day=int(start_day))
                    else:
                        start_timestamp = datetime.datetime(year=int(year), month=i+1, day=1)
                    end_timestamp = start_timestamp

                # if start_timestamp is not None and end_timestamp is not None:
                #     start_timestamp = str(start_timestamp)
                #     end_timestamp = str(end_timestamp)
                #     return start_timestamp, end_timestamp
                return start_timestamp, end_timestamp

if __name__ == '__main__':
    database_name = "dev"
    transformer = DataTransformer()
    transformed_venue_home = TransformedVenueHome(database_name)
    proceeding_home = ProceedingHome(database_name)
    none_dates = 0
    for p in proceeding_home.get_proceedings():
        proceeding = Proceeding(**p)
        occurrence, series = transformer.transform_proceeding(proceeding)
        transformed_venue_home.store_venue(occurrence)
        transformed_venue_home.store_venue(series)
        if occurrence["content"]["start_date"] is None:
            none_dates += 1
        else:
            # print(occurrence["content"]["conference_date"])
            pass

        # if 'akbc' in occurrence["content"]['dblp_key']:
        #     print(json.dumps(occurrence, indent=2))
        #     print(json.dumps(series, indent=2))
        # if 'hcomp' in occurrence['key']:
        #     print(json.dumps(occurrence, indent=2))
        #     print(json.dumps(series, indent=2))

    print("none_dates", none_dates)
    print("count", transformer.count)
    print("total", transformer.total)
    print("start_date_mismatch", transformer.start_date_mismatch)
    print("end_date_mismatch", transformer.end_date_mismatch)
    print("exceptions", transformer.exceptions)