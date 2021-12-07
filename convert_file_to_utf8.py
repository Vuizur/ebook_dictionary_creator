import json

with open("kaikki.org-dictionary-Spanish_new.json", "r", encoding="utf-8") as input, \
    open("spanish-dict-utf8_new.json", "w", encoding="utf-8") as out:
    for line in input:
        data = json.loads(line) 
        json.dump(data, out, ensure_ascii=False)
        out.write("\n")
    