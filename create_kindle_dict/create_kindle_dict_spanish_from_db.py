from pyglossary import Glossary
import sqlite3

def create_spanish_kindle_dict(source_database_path: str, input_language: str, output_language: str, output_path: str, author: str, title: str, try_to_fix_kindle_lookup_stupidity=False):
    Glossary.init()
    glos = Glossary()

    defiFormat = "h"

    con = sqlite3.connect(source_database_path)
    cur = con.cursor()
    print("Getting base forms")
    #TODO: This ignores words that have glosses, but are also base forms of other words
    #base_forms = cur.execute("SELECT w.word_id, w.word FROM word w WHERE w.word_id NOT IN (SELECT fow.word_id FROM form_of_word fow)").fetchall()
    base_forms = cur.execute("""SELECT word_id, word FROM word 
WHERE word.word_id IN (SELECT sense.word_id FROM sense) GROUP BY word
""").fetchall()
    
    inflection_num = 0
    counter = 0
    print("Iterating through base forms:")

    #This is needed to detect collisions between inflections ->
    #I don't yet know if the existence of one inflection stops the other from being found (but probably?)
    #TODO: Test with fui or fue

    all_inflections = []
    for word_id, canonical_form in base_forms:
        inflections = cur.execute("""SELECT w1.word FROM word w1
JOIN form_of_word fow ON fow.word_id = w1.word_id 
JOIN word w2 ON w2.word_id = fow.base_word_id 
WHERE w2.word = ?""", (canonical_form,)).fetchall()
        word_inflections = []
        for inflection in inflections:
            word_inflections.append(inflection[0])
        all_inflections.extend(list(set(word_inflections))) #Necessary because of too much form_of_word linkages

    for word_id, canonical_form in base_forms:
        counter = counter + 1
        #get inflections
        inflections = cur.execute("""SELECT w1.word FROM word w1
JOIN form_of_word fow ON fow.word_id = w1.word_id 
JOIN word w2 ON w2.word_id = fow.base_word_id 
WHERE w2.word = ?""", (canonical_form,)).fetchall()

        infl_list = []

        for inflection in inflections:
            if try_to_fix_kindle_lookup_stupidity and all_inflections.count(inflection[0]) > 1:
                #TODO: Finish once the pyglossary feature has been implemented
                #This should cause the creation of a new headword (if it works like I imagined)
                "fjdhf"
                #print(inflection[0])
            infl_list.append(inflection[0])
        infl_list = list(set(infl_list)) #TODO: Find out why there are duplicates here
        inflection_num += len(infl_list)
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
        #gloss_count = 1
        #TODO: add gloss count
        for gloss in glosses_list:
            glosshtml += "<p>" + gloss + "</p>"
        all_forms = [canonical_form]
        all_forms.extend(infl_list)
        glos.addEntryObj(glos.newEntry(all_forms, glosshtml, defiFormat))

        if counter % 2000 == 0:
            print(str(counter) + " words")
    print("Creating dictionary")
    glos.setInfo("title", title)
    glos.setInfo("author", author)
    glos.sourceLangName = input_language
    glos.targetLangName = output_language
    print("Writing dictionary")
    glos.write(output_path, format="Mobi", keep=True, exact=True, spellcheck=False, kindlegen_path="C:/Users/hanne/AppData/Local/Amazon/Kindle Previewer 3/lib/fc/bin/kindlegen.exe")
    #glos.write("spanish_dictionary.kobo", format="Kobo")
    print(str(len(base_forms)) + " base forms")
    print(str(inflection_num) + " inflections")
    cur.close()
    con.close()

if __name__ == "__main__":
    #create_kindle_dict_from_db()
    create_spanish_kindle_dict("spanish_dict.db", "Spanish", "English", "spanish_dict.mobi", "Vuizur", "Spanish-English Dictionary")