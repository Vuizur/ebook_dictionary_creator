from pyglossary import Glossary
import sqlite3
from unidecode import unidecode

from ebook_dictionary_creator.e_dictionary_creator.create_kindle_dict import Gloss, get_html_from_gloss_list

def create_nonkindle_dict(source_database_path: str, out_path: str, output_format: str, input_language=None, output_language=None, author: str = None, title: str = None):
    Glossary.init()
    glos = Glossary()

    defiFormat = "h"

    con = sqlite3.connect(source_database_path)
    cur = con.cursor()
    print("Getting base forms")
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

    for word_id, canonical_form in base_forms:
        counter = counter + 1

        glosses = cur.execute("""SELECT g.gloss_string, w.pos
FROM word w 
INNER JOIN sense s ON s.word_id = w.word_id 
INNER JOIN gloss g ON g.sense_id = s.sense_id 
WHERE w.word = ?""", (canonical_form,)).fetchall()

        glosses_list: list[Gloss] = []
        for gloss in glosses:
            if gloss[0] == None:
                continue
            glosses_list.append(Gloss(gloss[1], gloss[0].strip()))

        glosshtml = get_html_from_gloss_list(glosses_list)
        
        inflections = cur.execute("""SELECT w1.word FROM word w1
JOIN form_of_word fow ON fow.word_id = w1.word_id 
JOIN word w2 ON w2.word_id = fow.base_word_id 
WHERE w2.word = ?""", (canonical_form,)).fetchall()

        infl_list = []
        for inflection in inflections:
            infl_list.append(inflection[0])
        infl_list = list(set(infl_list)) #This has to do with a bug in the linkages that causes words to be doubly linked
            
        inflection_num += len(infl_list)
        
        all_forms = [canonical_form]
        all_forms.extend(infl_list)
        glos.addEntryObj(glos.newEntry(all_forms, glosshtml, defiFormat))

        if counter % 2000 == 0:
            print(str(counter) + " words")
    print("Creating dictionary")
    print("Writing dictionary")
    glos.setInfo("title", title)
    glos.setInfo("author", author)
    glos.sourceLangName = input_language
    glos.targetLangName = output_language

    if output_format == "Tabfile":
        glos.write(out_path, format="Tabfile")
    elif output_format == "Json":
        glos.write("json_test.json", format="Json")
        glos.write("diktjson_test.json", format="DiktJson")
    elif output_format == "Stardict":
        glos.write(out_path, format="Stardict")
    print(str(len(base_forms)) + " base forms")
    print(str(inflection_num) + " inflections")
    cur.close()
    con.close()