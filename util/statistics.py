from database.proceeding_home import ProceedingHome
from entity.proceeding import Proceeding
from collections import Counter
import json

proceeding_home = ProceedingHome()
conference_series = []
conference_occurrence = []
workshop_series = []
workshop_occurrence = []

# AKBC
    # invitation: Conference_Series
    # fullname: “Automated Knowledge Base Construction”
    # shortname: AKBC
# ICML/2017
    # invitation: Conference Occurrence
    # fullname: “International Conference on Machine Learning”
    # shortname: “ICML”
    # location: Seattle, WA
    # program_chairs:
    # parents: ICML

types = {}

for p in proceeding_home.get_proceedings():
    proceeding = Proceeding(**p)
    try:
        if "workshop" in proceeding.title.lower():
            workshop_series.append("/".join(proceeding.proceeding_key.split("/")[:-1]))
            workshop_occurrence.append(proceeding.proceeding_key)
            venue_type = "workshop"

            occurrence_instance = {}
            occurrence_instance["invitation_type"] = 'workshop_occurrence'
            occurrence_instance["title"] = proceeding.title
            occurrence_instance["location"] = ",".join(proceeding.title.split(",")[-3:]).strip()
            occurrence_instance["year"] = proceeding.year
            occurrence_instance["parent"] = "/".join(proceeding.proceeding_key.split("/")[:-1])
            occurrence_instance["program chairs"] = proceeding.editors
            occurrence_instance["publisher"] = proceeding.publisher
            occurrence_instance["external link"] = proceeding.ee
            occurrence_instance["book"] = proceeding.booktitle
            occurrence_instance["key"] = proceeding.proceeding_key
            occurrence_instance["dblp_url"] = proceeding.dblp_url

            series_instance = {}
            series_instance["invitation_type"] = 'workshop_series'
            series_instance["name"] = proceeding.conference_name
            series_instance["key"] = "/".join(proceeding.proceeding_key.split("/")[:-1])
            series_instance["short_name"] = proceeding.booktitle

            if "akbc" in proceeding.proceeding_key.lower():
                print(json.dumps(occurrence_instance, indent=2))
                print(json.dumps(series_instance, indent=2))

        else:
            conference_series.append("/".join(proceeding.proceeding_key.split("/")[1:-1]))
            conference_occurrence.append(proceeding.proceeding_key)
            venue_type = proceeding.proceeding_key.split("/")[0]

            occurrence_instance = {}
            occurrence_instance["invitation_type"] = 'conference_occurrence'
            occurrence_instance["title"] = proceeding.title
            occurrence_instance["location"] = ",".join(proceeding.title.split(",")[-3:]).strip()
            occurrence_instance["year"] = proceeding.year
            occurrence_instance["parent"] = "/".join(proceeding.proceeding_key.split("/")[:-1])
            occurrence_instance["program_chairs"] = proceeding.editors
            occurrence_instance["publisher"] = proceeding.publisher
            occurrence_instance["external_link"] = proceeding.ee
            occurrence_instance["key"] = proceeding.proceeding_key
            occurrence_instance["dblp_url"] = proceeding.dblp_url

            series_instance = {}
            series_instance["invitation_type"] = 'conference_series'
            series_instance["name"] = proceeding.conference_name
            series_instance["key"] = "/".join(proceeding.proceeding_key.split("/")[:-1])
            series_instance["short_name"] = proceeding.booktitle

            if "icml" in proceeding.proceeding_key.lower():
                print(json.dumps(occurrence_instance, indent=2))
                print(json.dumps(series_instance, indent=2))

        if venue_type not in types:
            types[venue_type] = []
        types[venue_type].append("/".join(proceeding.proceeding_key.split("/")[1:]))

    except Exception as e:
        print(proceeding.proceeding_key, e)

conference_series_counts = Counter(conference_series)
workshop_series_counts = Counter(workshop_series)
print (workshop_series_counts)
print (Counter(workshop_occurrence))

print(len(conference_series_counts))
print (len(conference_occurrence))
print(len(workshop_series_counts))
print (len(workshop_occurrence))

print(types.keys())
# print(types['journals'])

for type in types:
    print(type, types[type])
    series = []
    for proceeding in types[type]:
        series.append("/".join(proceeding.split("/")[:-1]))
    print(type, len(set(series)), len(types[type]))