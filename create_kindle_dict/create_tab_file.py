from pyglossary import Glossary
import sqlite3
from unidecode import unidecode
import collections

def create_tabfile(source_database_path: str,):
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

    #this serves to check overlappings with base forms
    base_forms_unidecoded = []
    for base_form in base_forms:
        base_forms_unidecoded.append(unidecode(base_form[1]))
    
    inflection_num = 0
    counter = 0
    print("Iterating through base forms:")

    if try_to_fix_kindle_lookup_stupidity:
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
                word_inflections.append(unidecode(inflection[0].lower()))
            all_inflections.extend(list(set(word_inflections))) #Necessary because of too much form_of_word linkages
    
        
        print("Count all elements: ")
        inflection_counts = collections.Counter(all_inflections)
        print("Elements counted")

    for word_id, canonical_form in base_forms:
        counter = counter + 1

        glosses = cur.execute("""SELECT g.gloss_string
FROM word w 
INNER JOIN sense s ON s.word_id = w.word_id 
INNER JOIN gloss g ON g.sense_id = s.sense_id 
WHERE w.word = ?""", (canonical_form,)).fetchall()

        glosses_list = []
        for gloss in glosses:
            if gloss[0] == None: #This appears to happen for some reason
                continue
            glosses_list.append(gloss[0].strip())
        glosses_list = list(set(glosses_list))
        glosshtml = ""
        #gloss_count = 1
        #TODO: add gloss count
        for gloss in glosses_list:
            glosshtml += "<p>" + gloss + "</p>"

        #get inflections
        inflections = cur.execute("""SELECT w1.word FROM word w1
JOIN form_of_word fow ON fow.word_id = w1.word_id 
JOIN word w2 ON w2.word_id = fow.base_word_id 
WHERE w2.word = ?""", (canonical_form,)).fetchall()

        infl_list = []
        for inflection in inflections:
            infl_list.append(inflection[0])
        infl_list = list(set(infl_list)) #This has to do with a bug in the linkages that causes words to be doubly linked
        already_separated_unidecoded_inflections = []

        rest_inflections = []
        for inflection in infl_list:
            unidecoded_inflection = unidecode(inflection)
            if try_to_fix_kindle_lookup_stupidity and (not unidecoded_inflection in already_separated_unidecoded_inflections) \
                 and ((unidecoded_inflection.lower() in base_forms_unidecoded) or (inflection_counts[inflection] > 1)):
                #these forms will otherwise not be found by the stupid algorithm
                pgl_list = ["HTML_HEAD<b>" + canonical_form + "</b>", inflection]
                glos.addEntryObj(glos.newEntry(pgl_list, glosshtml, defiFormat))
                already_separated_unidecoded_inflections.append(unidecoded_inflection)
            else:
                rest_inflections.append(inflection)
        
        inflection_num += len(infl_list)
        
        all_forms = ["HTML_HEAD<b>" + canonical_form + "</b>", canonical_form]
        all_forms.extend(rest_inflections)
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