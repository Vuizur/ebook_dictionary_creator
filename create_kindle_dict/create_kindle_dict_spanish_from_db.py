from pyglossary import Glossary
import sqlite3

def create_spanish_kindle_dict():
    Glossary.init()
    glos = Glossary()

    defiFormat = "h"

    con = sqlite3.connect("spanish_dict.db")
    cur = con.cursor()
    print("Getting base forms")
    #TODO: This ignores words that have glosses, but are also base forms of other words -> Fix this!
    base_forms = cur.execute("SELECT w.word_id, w.word FROM word w WHERE w.word_id NOT IN (SELECT fow.word_id FROM form_of_word fow)").fetchall()
    base_forms_no_dupes = []
    #TODO: This removes meanings of words!
    already_used_forms = []
    print("Eliminating duplicates")
    for word_id, canonical_form in base_forms:
        if canonical_form in already_used_forms:
            continue
        else:
            base_forms_no_dupes.append((word_id, canonical_form))
            already_used_forms.append(canonical_form)

    base_forms = base_forms_no_dupes
    print(str(len(base_forms)) + " base forms")
    counter = 0
    print("Iterating through base forms:")
    for word_id, canonical_form in base_forms:
        counter = counter + 1
        #get inflections
        #TODO: get alternative canonical form as inflection as well
        #and add all unaccented versions as inflection as well

        inflections = cur.execute("""SELECT w1.word FROM word w1
JOIN form_of_word fow ON fow.word_id = w1.word_id 
JOIN word w2 ON w2.word_id = fow.base_word_id 
WHERE w2.word = ?""", (canonical_form,)).fetchall()

        infl_list = []

        for inflection in inflections:
            infl_list.append(inflection[0])
        infl_list = list(set(infl_list)) #TODO: Find out why there are duplicates here
        glosses = cur.execute("""SELECT g.gloss_string
FROM word w 
INNER JOIN sense s ON s.word_id = w.word_id 
INNER JOIN gloss g ON g.sense_id = s.sense_id 
WHERE w.word = ?""", (canonical_form,)).fetchall()

        glosses_list = []
        for gloss in glosses:
            if gloss[0] == None: #This appears to happen for some reason
                continue
            glosses_list.append(gloss[0])

        glosshtml = ""
        gloss_count = 1
        #TODO: add gloss count
        for gloss in glosses_list:
            glosshtml += "<p>" + gloss + "</p>"
        all_forms = [canonical_form]
        all_forms.extend(infl_list)
        glos.addEntryObj(glos.newEntry(all_forms, glosshtml, defiFormat))

        if counter % 2000 == 0:
            print(str(counter) + " words")
    print("Creating dictionary")
    glos.setInfo("title", "Spanish-English Dictionary")
    glos.setInfo("author", "Vuizur")
    glos.sourceLangName = "Spanish"
    glos.targetLangName = "English"
    print("Writing dictionary")
    glos.write("spanish_dict.mobi", format="Mobi", keep=True, exact=True, spellcheck=False, kindlegen_path="C:/Users/hanne/AppData/Local/Amazon/Kindle Previewer 3/lib/fc/bin/kindlegen.exe")
    #glos.write("spanish_dictionary.kobo", format="Kobo")

if __name__ == "__main__":
    #create_kindle_dict_from_db()
    create_spanish_kindle_dict()