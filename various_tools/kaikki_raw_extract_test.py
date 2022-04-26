import json

def extract_russian_part():
    with open("D:/raw-wiktextract-data.json", "r", encoding="utf-8") as f, \
         open("D:/raw-wiktextract-data_russian.json", "w", encoding="utf-8") as out:
    
        for line in f:
            obj = json.loads(line)
            if "lang" in obj and obj["lang"] == "Russian":
                out.write(line)
