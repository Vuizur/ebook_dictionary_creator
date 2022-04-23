import json
with open("D:/raw-wiktextract-data.json", "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        if "word" in obj and obj["word"] == "писать":
            print(obj)
            print("#\n")