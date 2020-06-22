from database.proceeding_home import ProceedingHome
from entity.proceeding import Proceeding
from collections import Counter
import json

database = "test_database2"
proceeding_home = ProceedingHome(database)
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
books = []

for p in proceeding_home.get_proceedings():
    proceeding = Proceeding(**p)
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

        series_instance = {}
        series_instance["invitation_type"] = invitation_type + '_series'
        series_instance["name"] = proceeding.conference_name
        series_instance["key"] = "/".join(proceeding.proceeding_key.split("/")[:-1])
        series_instance["short_name"] = series_name.upper()

        # books.append(proceeding.booktitle)

        if proceeding.parent_link is not None:
            # Mapping 'https://dblp.org/db/conf/nips/index.html' => 'conf/nips'
            parent = proceeding.parent_link.split("https://dblp.org/db/")[1]  # => conf/nips/index.html
            parent = "/".join(parent.split("/")[:-1])  # => conf/nips
            parent += "/" + proceeding.year  # => conf/nips/2017
            occurrence_instance["parent"].append(parent)

        if "akbc" in proceeding.proceeding_key.lower():
            print(json.dumps(occurrence_instance, indent=2))
            print(json.dumps(series_instance, indent=2))

        if venue_type not in types:
            types[venue_type] = []
        types[venue_type].append("/".join(proceeding.proceeding_key.split("/")[1:]))

    except Exception as e:
        print(proceeding.proceeding_key, e)

conference_series_counts = Counter(conference_series)
workshop_series_counts = Counter(workshop_series)
book_counts = Counter(books)
print("workshop_series_counts", workshop_series_counts)
print("conference_series_counts", conference_series_counts)
# print (Counter(workshop_occurrence))
print("book_counts", book_counts)

print(len(conference_series_counts))
print(len(conference_occurrence))
print(len(workshop_series_counts))
print(len(workshop_occurrence))

print(types.keys())
# print(types['journals'])

for type in types:
    print(type, types[type])
    series = []
    for proceeding in types[type]:
        series.append("/".join(proceeding.split("/")[:-1]))
    print(type, len(set(series)), len(types[type]))

# 'The 4th Human Computation Workshop, HCOMP@AAAI 2012, Toronto, Ontario, Canada, July 23, 2012.'
