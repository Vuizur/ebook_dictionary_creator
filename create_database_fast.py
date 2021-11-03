import json
import sqlite3
import time
import os
from add_openrussian_to_database import add_openrussian_to_db
import remove_accents


def append_form_to_record(form: dict, form_dict:dict):
    form_tags = form["tags"]
    word_form = form["form"]

    if len(form_tags) == 2 and (("nominative" in form_tags and "plural" in form_tags) or ("genitive" in form_tags and "plural")):
        if "nominative" in form_tags and "plural" in form_tags:
            form_dict["nominative_plural_form"] = word_form
        elif "genitive" in form_tags and "plural" in form_tags:
            form_dict["genitive_plural_form"] = word_form
    else:
        for form_tag in form_tags:
            if form_tag == "canonical":
                form_dict["canonical_form"] = word_form
            elif form_tag == "romanization":
                form_dict["romanized_form"] = word_form
            elif form_tag == "genitive":
                form_dict["genitive_form"] = word_form
            elif form_tag == "adjective":
                form_dict["adjective_form"] = word_form
try:
    os.remove("words4.db")
except:
    pass
with open('create_db_tables.sql', 'r') as sql_file:
    sql_script = sql_file.read()

con = sqlite3.connect('words4.db')
cur = con.cursor()
cur.executescript(sql_script)

con.commit()

with open("russian-dict-utf8_2.json", "r", encoding="utf-8") as f:

    form_of_words_to_add_later: "list[tuple(int, str)]" = []
    for line in f:

        obj = json.loads(line)

        form_col = None
        form_string = None
        word_ipa_pronunciation = None
        pos = None
        form_dict: dict[str, str] = {
        "canonical_form": None,
        "romanized_form": None,
        "genitive_form": None,
        "adjective_form": None,
        "nominative_plural_form": None,
        "genitive_plural_form": None
        }
        ipa_pronunciation = None
        lang = None
        word = None
        lang_code = None

        word_pos = obj["pos"]
        try:
            for form in obj["forms"]:
                append_form_to_record(form, form_dict)
        except:
            #print("Error for word")
            pass
        try:
            word_ipa_pronunciation = obj["sounds"][0]["ipa"]
        except:
            pass
        
        #remove everything after the first word because canonical forms are currently bugged in the wiktionary data
        #this creates inconsistent data, but for looking up the stress only words without space matter
        #TODO: fix and hope it gets solved upstream
        try:
            canonical_form_split = form_dict["canonical_form"].split(" ")
            #fix those wrong strings like балда f inan 
            if len(canonical_form_split[1]) == 1:
                form_dict["canonical_form"] = canonical_form_split[0]
        except:
            pass

        word_lang = obj["lang"]
        word_lang_code = obj["lang_code"]
        word_word = obj["word"]
        word_lowercase = word_word.lower()
        word_without_yo = word_lowercase.replace("ё", "е")
        try:
            if len(obj["senses"]) <= 1 and "Russian spellings with е instead of ё" in obj["senses"][0]["categories"]:
                continue
        except:
            pass

        cur.execute("INSERT INTO word (pos, canonical_form, romanized_form, genitive_form, adjective_form, nominative_plural_form, \
            genitive_plural_form, ipa_pronunciation, lang, word, lang_code, word_lowercase, word_lower_and_without_yo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (word_pos, form_dict["canonical_form"], form_dict["romanized_form"], form_dict["genitive_form"], form_dict["adjective_form"]\
            , form_dict["nominative_plural_form"], form_dict["genitive_plural_form"], word_ipa_pronunciation, word_lang, word_word, word_lang_code, word_lowercase, word_without_yo))
        
        word_id = cur.lastrowid
        #word_id, base_word_string
        

        for sense in obj["senses"]:
            try:
                if "Russian spellings with е instead of ё" in sense["categories"]:
                    #print(word_word)
                    continue
            except:
                pass
            
            if "form_of" in sense:
                for base_word in sense["form_of"]:
                    form_of_words_to_add_later.append((word_id, base_word["word"]))
                cur.execute("INSERT INTO sense (word_id) VALUES (?)", (word_id,))
                sense_id = cur.lastrowid
                try:
                    for gloss in sense["glosses"]:
                        gloss_sense_id = sense_id
                        gloss_string = gloss
                        cur.execute("INSERT INTO gloss (sense_id, word_case) VALUES(?, ?)", (gloss_sense_id, gloss_string))
                except:
                    pass
                #todo: fix for glosses that aren't the base word (pretty rare case)
            else:
                cur.execute("INSERT INTO sense (word_id) VALUES (?)", (word_id,))
                sense_id = cur.lastrowid
                try:
                    for gloss in sense["glosses"]:
                        gloss_sense_id = sense_id
                        gloss_string = gloss
                        cur.execute("INSERT INTO gloss (sense_id, gloss_string, word_case) VALUES(?, ?, \"nominative\")", (gloss_sense_id, gloss_string))
                except:
                    pass
       
    con.commit()
        #add form of words after all data has been inserted

    with open("forms_to_add_later.json", 'w', encoding="utf-8") as f:
    # indent=2 is not needed but makes the file human-readable
        json.dump(form_of_words_to_add_later, f, indent=2, ensure_ascii=False) 

    cur.execute("CREATE INDEX word_word_index ON word(word);")
    cur.execute("CREATE INDEX word_canonical_form_index ON word(canonical_form);")
    cur.execute("CREATE INDEX word_lowercase_index ON word(word_lowercase);")
    cur.execute("CREATE INDEX word_lower_and_without_yo_index ON word(word_lower_and_without_yo);")
    cur.execute("CREATE INDEX sense_word_id_index ON sense(word_id);")
    cur.execute("CREATE INDEX gloss_sense_id_index ON gloss(sense_id);")


    con.commit()
    records = []
    t0 = time.time()

    for index in range(0, len(form_of_words_to_add_later), 1000):

        for word_id, base_word in form_of_words_to_add_later[index: index+1000]:
            unaccented_word = remove_accents.unaccentify(base_word)

            cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) \
SELECT ?, COALESCE ( \
(SELECT w.word_id FROM word w WHERE w.word = ?), \
(SELECT w.word_id FROM word w WHERE w.canonical_form = ?), \
(SELECT w.word_id FROM word w WHERE w.word = ?) \
)", (word_id, base_word, base_word, unaccented_word))


    t1 = time.time()
    print(t1 - t0)


con.commit()
con.close()
add_openrussian_to_db()
