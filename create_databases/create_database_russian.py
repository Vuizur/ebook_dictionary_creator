import json
import sqlite3
import time
import os
from create_databases.add_openrussian_to_database import add_openrussian_to_db
from helper_functions import has_cyrillic_letters, remove_weird_characters_for_alternative_canonical, unaccentify, remove_accent_if_only_one_syllable
import re

DO_NOT_ADD_GRAMMAR_INFO = True #Set true to reduce size of DB

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
            if form_tag == "canonical" and form_dict["canonical_form"] == None:
                form_dict["canonical_form"] = word_form
            elif form_tag == "canonical":
                form_dict["alternative_canonial_form"] = remove_weird_characters_for_alternative_canonical(word_form)
            elif form_tag == "romanization":
                form_dict["romanized_form"] = word_form
            elif form_tag == "genitive":
                form_dict["genitive_form"] = word_form
            elif form_tag == "adjective":
                form_dict["adjective_form"] = word_form

def create_database_russian(database_path: str, wiktextract_json_path: str):
    try:
        os.remove(database_path)
    except:
        pass
    with open('create_databases/create_db_tables_russian.sql', 'r') as sql_file:
        sql_script = sql_file.read()

    con = sqlite3.connect(database_path)
    cur = con.cursor()
    cur.executescript(sql_script)

    con.commit()

    alternative_yo_pattern = re.compile(".*Alternative spelling.*ё")

    with open(wiktextract_json_path, "r", encoding="utf-8") as f:
        #tuple structure: word_id, base_word_string, grammar case
        form_of_words_to_add_later: "list[tuple(int, str, str)]" = []
        for line in f:

            obj = json.loads(line)

            word_ipa_pronunciation = None
            form_dict: dict[str, str] = {
            "canonical_form": None,
            "alternative_canonial_form": None,
            "romanized_form": None,
            "genitive_form": None,
            "adjective_form": None,
            "nominative_plural_form": None,
            "genitive_plural_form": None
            }

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
            
            #skip all words where canonical_form does not have cyrillic letters because most likely it is something wrong like "n inan f"
            #and
            #check if Alternative spelling is in canonical form and then if a ё follows. If this is true, ignore word
            if form_dict["canonical_form"] != None and (alternative_yo_pattern.match(form_dict["canonical_form"]) != None or
                not has_cyrillic_letters(form_dict["canonical_form"])):
                continue

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

            word_word = obj["word"]
            word_lowercase = word_word.lower()
            word_without_yo = word_lowercase.replace("ё", "е")

            if form_dict["canonical_form"] != None:
                form_dict["canonical_form"] = remove_accent_if_only_one_syllable(form_dict["canonical_form"])
            else:
                form_dict["canonical_form"] = word_word

            try:
                #this could theoretically remove valid words from the library if there is a ё-version of them, but I am not
                #convinced that this is a problem -- Update: This is a problem if you look at the base category, but this version with 
                #the senses might be safe. I should probably remove this entire block of code TODO: fix
                if "Russian spellings with е instead of ё" in obj["senses"][0]["categories"]:
                    continue
            except:
                pass
            

            cur.execute("INSERT INTO word (pos, canonical_form, alternative_canonical_form, romanized_form, \
                ipa_pronunciation, word, word_lowercase, word_lower_and_without_yo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (word_pos, form_dict["canonical_form"], form_dict["alternative_canonial_form"], form_dict["romanized_form"], \
               word_ipa_pronunciation, word_word, word_lowercase, word_without_yo))

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
                        tag_string: str = ""
                        for tag in sense["tags"]:
                            tag_string += tag + " "

                        form_of_words_to_add_later.append((word_id, base_word["word"], tag_string))
                    cur.execute("INSERT INTO sense (word_id) VALUES (?)", (word_id,))
                    sense_id = cur.lastrowid
                    try:
                        for gloss in sense["glosses"]:
                            if DO_NOT_ADD_GRAMMAR_INFO:
                                gloss = None

                            cur.execute("INSERT INTO gloss (sense_id, word_case) VALUES(?, ?)", (sense_id, gloss))
                    except:
                        pass
                    #todo: fix for glosses that aren't the base word (pretty rare case)
                else:
                    cur.execute("INSERT INTO sense (word_id) VALUES (?)", (word_id,))
                    sense_id = cur.lastrowid
                    try:
                        for gloss in sense["glosses"]:
                            if DO_NOT_ADD_GRAMMAR_INFO:
                                gloss = None
                            cur.execute("INSERT INTO gloss (sense_id, gloss_string, word_case) VALUES(?, ?, \"nominative\")", (sense_id, gloss))
                    except:
                        pass
                    
        con.commit()
            #add form of words after all data has been inserted

        #with open("forms_to_add_later.json", 'w', encoding="utf-8") as f:
        ## indent=2 is not needed but makes the file human-readable
        #    json.dump(form_of_words_to_add_later, f, indent=2, ensure_ascii=False) 

        cur.execute("CREATE INDEX word_word_index ON word(word);")
        cur.execute("CREATE INDEX word_canonical_form_index ON word(canonical_form);")
        cur.execute("CREATE INDEX alternative_word_canonical_form_index ON word(alternative_canonical_form);")

        cur.execute("CREATE INDEX word_lowercase_index ON word(word_lowercase);")
        cur.execute("CREATE INDEX word_lower_and_without_yo_index ON word(word_lower_and_without_yo);")
        cur.execute("CREATE INDEX sense_word_id_index ON sense(word_id);")
        cur.execute("CREATE INDEX gloss_sense_id_index ON gloss(sense_id);")
        cur.execute("CREATE INDEX word_id_index ON form_of_word(word_id);")
        cur.execute("CREATE INDEX base_word_id_index ON form_of_word(base_word_id);")

        con.commit()
        records = []
        t0 = time.time()

        for index in range(0, len(form_of_words_to_add_later), 1000):

            for word_id, base_word, case_text in form_of_words_to_add_later[index: index+1000]:
                unaccented_word = unaccentify(base_word)

                cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) \
    SELECT ?, COALESCE ( \
    (SELECT w.word_id FROM word w WHERE w.word = ?), \
    (SELECT w.word_id FROM word w WHERE w.canonical_form = ?), \
    (SELECT w.word_id FROM word w WHERE w.word = ?) \
    )", (word_id, base_word, base_word, unaccented_word))
                form_of_word_id = cur.lastrowid
                cur.execute("INSERT OR IGNORE INTO gramm_case (form_of_word_id, case_text) VALUES (?,?)", (form_of_word_id, case_text))


        t1 = time.time()
        print(t1 - t0)


    con.commit()
    con.close()