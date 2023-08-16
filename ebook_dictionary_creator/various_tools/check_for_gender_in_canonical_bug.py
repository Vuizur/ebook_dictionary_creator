# Open kaikki.org-dictionary-Russian.json and iterate through lines

import json
import os
from stressed_cyrillic_tools import unaccentify

with open("kaikki.org-dictionary-Russian.json", "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)


        #try:
        if "forms" in obj:
            for form in obj["forms"]:
                if "tags" in form and "canonical" in form["tags"]:

                    if unaccentify(form["form"]) != obj["word"]:
                        print(form["form"])
                        print(obj["word"])

                    #split_form = form["form"].split(" ")
                    #if len(split_form) > 1 and len(split_form[1]) == 1:
                    #    print(form)
                        #print(split_form)
                        #print(obj["word"])
                        #print(obj["forms"])
                        #print("\n")
                        
