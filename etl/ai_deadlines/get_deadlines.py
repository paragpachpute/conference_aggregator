import yaml
import json
import urllib.request

from database.deadline_home import DeadlineHome

url = "https://raw.githubusercontent.com/abhshkdz/ai-deadlines/gh-pages/_data/conferences.yml"
urllib.request.urlretrieve(url, "resources/conferences.yml")

with open("resources/conferences.yml") as f:
    deadlines = yaml.load(f, Loader=yaml.FullLoader)
    deadline_home = DeadlineHome(database_name="dev")
    deadline_home.store_many_deadlines(deadlines)
    print(json.dumps(deadlines, indent=2))
    print(len(deadlines))