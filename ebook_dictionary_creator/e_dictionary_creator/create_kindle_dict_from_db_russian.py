from os import path
import sqlite3
from pyglossary.glossary import Glossary

from stressed_cyrillic_tools import remove_yo, unaccentify

def create_py_glossary_and_export(database_path, format="MOBI"):
    Glossary.init()
    glos = Glossary()

    defiFormat = "h"

    con = sqlite3.connect(database_path)
    cur = con.cursor()
    
    base_forms = cur.execute("""SELECT w.word_id, w.canonical_form FROM word w
WHERE w.word_id IN (SELECT sense.word_id FROM sense) GROUP BY w.canonical_form
""").fetchall()

    print(str(len(base_forms)) + " base forms")
    f =  open("removed_glosses.txt", "w", encoding="utf-8")

    phrases_mistaken = set()

    counter = 0
    for word_id, canonical_form in base_forms:
        counter = counter + 1
        
        #get inflections
        #TODO: get alternative canonical form as inflection as well

        inflections = cur.execute("""SELECT w1.canonical_form FROM word w1
JOIN form_of_word fow ON fow.word_id = w1.word_id 
JOIN word w2 ON w2.word_id = fow.base_word_id 
WHERE w2.canonical_form = ?""", (canonical_form,)).fetchall()

        infl_list = []
        infl_list.append(remove_yo(canonical_form))
        infl_list.append(unaccentify(remove_yo(canonical_form)))
        
        for inflection in inflections:
            infl_list.append(inflection[0])
            infl_list.append(remove_yo(inflection[0]))
            infl_list.append(unaccentify(remove_yo(inflection[0])))

        infl_list = list(set(infl_list)) #TODO: Find out why there are duplicates here
        if canonical_form in infl_list:
            infl_list.remove(canonical_form)
        glosses = cur.execute("""SELECT g.gloss_string, g.gloss_lang
FROM word w 
INNER JOIN sense s ON s.word_id = w.word_id 
INNER JOIN gloss g ON g.sense_id = s.sense_id 
WHERE w.canonical_form = ?""", (canonical_form,)).fetchall()

        glosses_list: list[str] = []
        for gloss, gloss_lang in glosses:

            if gloss.strip() == "" or gloss == None or gloss_lang != "en": 
                continue
            glosses_list.append(gloss)

        if glosses_list == []:
            continue

        glosshtml = ""
        for gloss in glosses_list:
            glosshtml += "<p>" + gloss + "</p>"
        all_forms = [canonical_form]
        all_forms.extend(infl_list)
        glos.addEntryObj(glos.newEntry(all_forms, glosshtml, defiFormat))
        if counter % 2000 == 0:
            print(str(counter) + " words")
    glos.setInfo("title", "Russian-English Dictionary")
    glos.setInfo("author", "Vuizur")
    glos.sourceLangName = "Russian"
    glos.targetLangName = "English"
    #Spellcheck set to false because not supported for Russian
    if format == "MOBI":
        glos.write("test.mobi", format="Mobi", keep=True, exact= True, spellcheck=False, kindlegen_path="C:/Users/hanne/AppData/Local/Amazon/Kindle Previewer 3/lib/fc/bin/kindlegen.exe")
        #I don't know why the result does not work, I guess it is because of the combining accent symbol

    elif format == "STARDICT":
        glos.write("russian.ifo", format="Stardict")
    elif format == "TABFILE":
        glos.write("russian.txt", format="Tabfile")


    for phrase in phrases_mistaken:
        f.write(phrase + "\n")
    f.close()