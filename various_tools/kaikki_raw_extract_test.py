import json



def extract_russian_part():
    with open("D:/raw-wiktextract-data.json", "r", encoding="utf-8") as f, \
         open("raw-wiktextract-data_russian_new.json", "w", encoding="utf-8") as out:
    
        for line in f:
            obj = json.loads(line)
            if "lang" in obj and obj["lang"] == "Russian":
                out.write(line)

if __name__ == "__main__":
    extract_russian_part()