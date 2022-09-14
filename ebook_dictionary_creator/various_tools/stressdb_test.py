import json


with open("stressdb.json", "r") as file, open(
    "stressdb_test.json", "w", encoding="utf-8"
) as out:
    jsonf = json.load(file)
    out.write(json.dumps(jsonf, ensure_ascii=False, indent=4))
