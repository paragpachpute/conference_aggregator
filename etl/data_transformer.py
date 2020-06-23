import os
import logging

log = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class DataTransformer:
    def __init__(self):
        pass

    def transform_proceeding(self, proceeding):
        try:
            if "workshop" in proceeding.title.lower():
                invitation_type = 'workshop'
            else:
                invitation_type = 'series'

            series_name = "/".join(proceeding.proceeding_key.split("/")[1:-1])
            venue_type = proceeding.proceeding_key.split("/")[0]

            occurrence_instance = {}
            occurrence_instance["invitation_type"] = invitation_type + '_occurrence'
            occurrence_instance["title"] = proceeding.title
            occurrence_instance["location"] = ",".join(proceeding.title.split(",")[-3:]).strip()
            occurrence_instance["year"] = proceeding.year
            occurrence_instance["parent"] = []
            occurrence_instance["parent"].append("/".join(proceeding.proceeding_key.split("/")[:-1]))
            occurrence_instance["program chairs"] = proceeding.editors
            occurrence_instance["publisher"] = proceeding.publisher
            occurrence_instance["external link"] = proceeding.ee
            occurrence_instance["book"] = proceeding.booktitle
            occurrence_instance["key"] = proceeding.proceeding_key
            occurrence_instance["dblp_url"] = proceeding.dblp_url
            occurrence_instance["_id"] = [occurrence_instance["invitation_type"], occurrence_instance["key"]]

            series_instance = {}
            series_instance["invitation_type"] = invitation_type + '_series'
            series_instance["name"] = proceeding.conference_name
            series_instance["key"] = "/".join(proceeding.proceeding_key.split("/")[:-1])
            series_instance["short_name"] = series_name.upper()
            series_instance["_id"] = [series_instance["invitation_type"], series_instance["key"]]

            if proceeding.parent_link is not None:
                # Mapping 'https://dblp.org/db/conf/nips/index.html' => 'conf/nips/2017'
                parent = proceeding.parent_link.split("https://dblp.org/db/")[1]  # => conf/nips/index.html
                parent = "/".join(parent.split("/")[:-1])  # => conf/nips
                parent += "/" + proceeding.year  # => conf/nips/2017
                occurrence_instance["parent"].append(parent)

            return occurrence_instance, series_instance

        except Exception as e:
            log.error(
                "Failed while doing proceeding transformation for {} with error: {}".format(proceeding.proceeding_key,
                                                                                            e))
