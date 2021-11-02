import json

with open("kaikki.org-dictionary-Russian.json", "r", encoding="utf-8") as input, \
    open("russian-dict-utf8_3.json", "w", encoding="utf-8") as out:
    for line in input:
        data = json.loads(line) 
        json.dump(data, out, ensure_ascii=False)
        out.write("\n")
    