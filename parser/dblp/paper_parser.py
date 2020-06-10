import json

with open('proceeding_papers.json') as json_file:
    obj = json.loads(json_file.read())
    result = obj['result']
    hits = result['hits']
    print(len(hits['hit']))
    # print(json.dumps(obj, indent=2))