import json
import sqlite3
from sqlite3.dbapi2 import Cursor
import time
import os
from enum import Enum

#TODO: This should be cleaned up/almost entirely removed
def append_form_to_record(form: dict, form_dict:dict):
    form_tags = form["tags"]
    word_form = form["form"]
    if len(form_tags) == 1:
        if form_tags[0] == "canonical":
            form_dict["canonical_form"] = word_form
        elif form_tags[0] == "romanization":
            form_dict["romanized_form"] = word_form
        elif form_tags[0] == "genitive":
            form_dict["genitive_form"] = word_form
        elif form_tags[0] == "adjective":
            form_dict["adjective_form"] = word_form
        else:
            pass
            #print("unknown form")
            #print(form_tags[0])
    elif len(form_tags) == 2:
        if "nominative" in form_tags and "plural" in form_tags:
            form_dict["nominative_plural_form"] = word_form
        elif "genitive" in form_tags and "plural" in form_tags:
            form_dict["genitive_plural_form"] = word_form
        else:
            pass
            #print("unknown form with 2 tags:")
            #print(form_tags)
    else:
        pass
        #print("unknown form with strange number of tags:")
        #print(form_tags)
def create_indices(cur: Cursor):
        cur.execute("CREATE INDEX word_word_index ON word(word);")
        cur.execute("CREATE INDEX sense_word_id_index ON sense(word_id);")
        cur.execute("CREATE INDEX gloss_sense_id_index ON gloss(sense_id);")
        #These following indices are not included in the primary key designation and extremely necessary
        cur.execute("CREATE INDEX word_id_index ON form_of_word(word_id);")
        cur.execute("CREATE INDEX base_word_id_index ON form_of_word(base_word_id);")

def insert_base_linkages(form_of_words_to_add_later: "list[tuple(int, str)]", cur: Cursor):
    for index in range(0, len(form_of_words_to_add_later), 10000):
    #for form_of_entry in form_of_words_to_add_later:
        for word_id, base_word in form_of_words_to_add_later[index: index+10000]:
            cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) \
SELECT ?, (SELECT w.word_id FROM word w WHERE w.word = ?)", (word_id, base_word))

def add_linkages_to_spanish_compound_words(cur: Cursor):
    compound_words = cur.execute("""
    SELECT w.word_id, s.sense_id, g.gloss_id, g.gloss_string 
    FROM word w 
    INNER JOIN sense s ON s.word_id = w.word_id 
    INNER JOIN gloss g ON g.sense_id = s.sense_id 
    WHERE g.gloss_string LIKE "Compound of the%"
    """).fetchall()

    for word_id, sense_id, gloss_id, gloss_string in compound_words:
        if "compound of the infinitive" in gloss_string.lower():
            #let's hope this works for all infinitive cases, but maybe notS
            string_sliced = gloss_string[27:]
            base_word = string_sliced.split(" ")[0]
            #This could be customized to match only verbs, but I'll leave it like that for now
            cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) \
SELECT ?, (SELECT w.word_id FROM word w WHERE w.word = ?)", (word_id, base_word))
        elif "imperative form of" in gloss_string:
            base_word = gloss_string.split("imperative form of ", 1)[1].replace(",", " and ").split(" and ")[0]
            cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) \
SELECT ?, (SELECT w.word_id FROM word w WHERE w.word = ?)", (word_id, base_word))
            cur.execute("DELETE FROM gloss WHERE gloss_id = ?", (gloss_id,))
        elif " the preterite " in gloss_string:
            pret_base_word = gloss_string.split(" the preterite ", 1)[1].replace(",", " and ").split(" and ")[0]
            #TODO: Fix for special cases where there are two options
            try:
                base_word = cur.execute("""
                SELECT w2.word 
    FROM word w1
    JOIN form_of_word fow ON w1.word_id = fow.word_id
    JOIN word w2 ON w2.word_id = fow.base_word_id 
    WHERE w1.word = ?
                """, (pret_base_word,)).fetchone()[0]
            except Exception as e:
                print(e)
            #print(pret_base_word)
            #print(base_word)
            cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) \
            SELECT ?, (SELECT w.word_id FROM word w WHERE w.word = ?)", (word_id, base_word))
        elif " indicative form " in gloss_string:
            base_word = gloss_string.split(" indicative form ", 1)[1].replace(",", " and ").split(" and ")[0]
            cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) \
            SELECT ?, (SELECT w.word_id FROM word w WHERE w.word = ?)", (word_id, base_word))
        elif " subjunctive form of " in gloss_string:
            base_word = gloss_string.split(" subjunctive form of ", 1)[1].replace(",", " and ").split(" and ")[0]
            cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) \
            SELECT ?, (SELECT w.word_id FROM word w WHERE w.word = ?)", (word_id, base_word))
        elif " participle of " in gloss_string:
            base_word = gloss_string.split(" participle of ", 1)[1].replace(",", " and ").split(" and ")[0]
            cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) \
            SELECT ?, (SELECT w.word_id FROM word w WHERE w.word = ?)", (word_id, base_word))
        elif " form of the verb " in gloss_string:
            base_word = gloss_string.split(" form of the verb ", 1)[1].replace(",", " and ").split(" and ")[0]
            cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) \
            SELECT ?, (SELECT w.word_id FROM word w WHERE w.word = ?)", (word_id, base_word))
        elif " of the imperfect " in gloss_string:
            imp_base_word = gloss_string.split(" of the imperfect ", 1)[1].replace(",", " and ").split(" and ")[0]
            #TODO: Fix for special cases where there are two options
            try:
                base_word = cur.execute("""
                SELECT w2.word 
    FROM word w1
    JOIN form_of_word fow ON w1.word_id = fow.word_id
    JOIN word w2 ON w2.word_id = fow.base_word_id 
    WHERE w1.word = ?
                """, (imp_base_word,)).fetchone()[0]
            except Exception as e:
                print(e)
                print(gloss_string)
        elif " of the present indicative " in gloss_string:
            pi_base_word = gloss_string.split(" of the present indicative ", 1)[1].replace(",", " and ").split(" and ")[0]
            #TODO: Fix for special cases where there are two options
            try:
                base_word = cur.execute("""
                SELECT w2.word 
    FROM word w1
    JOIN form_of_word fow ON w1.word_id = fow.word_id
    JOIN word w2 ON w2.word_id = fow.base_word_id 
    WHERE w1.word = ?
                """, (pi_base_word,)).fetchone()[0]
            except Exception as e:
                print(e)
                print(gloss_string)
        elif " conditional form of " in gloss_string:
            c_base_word = gloss_string.split(" conditional form of ", 1)[1].replace(",", " and ").split(" and ")[0]
            #TODO: Fix for special cases where there are two options
            try:
                base_word = cur.execute("""
                SELECT w2.word 
    FROM word w1
    JOIN form_of_word fow ON w1.word_id = fow.word_id
    JOIN word w2 ON w2.word_id = fow.base_word_id 
    WHERE w1.word = ?
                """, (c_base_word,)).fetchone()[0]
            except Exception as e:
                print(e)
                print(gloss_string)
        else:
            print(word_id)
            print(gloss_string)
        cur.execute("DELETE FROM gloss WHERE gloss_id = ?", (gloss_id,))
        cur.execute("DELETE FROM sense WHERE sense_id = ?", (sense_id,))

    

def delete_unneeded_entries(cur: Cursor, delete_words_without_chars = True, delete_words_beginning_or_ending_with_minus = True, 
    delete_sur_given_names = True, delete_entries_with_space = False, delete_cities_towns = True):
    
    #TODO: finish
    #place_signifiers = ["a city", "a town", "a province", "the capital city", "a neighbourhood", "a state", "a canton of"]


    word_ids = cur.execute("SELECT w.word_id, w.word FROM word w").fetchall()
    if delete_words_without_chars:
        for word_id, word in word_ids:
            if not word.upper().isupper():
                print(word)
                cur.execute("DELETE FROM word WHERE word_id = ?", (word_id,))
    #if delete_cities_towns:
    #    for word_id, word in word_ids:
    #        if 
    
    cur.execute("DELETE FROM word WHERE pos = \"circumfix\"")
    if delete_sur_given_names:
        name_tuple = cur.execute(f"""
SELECT s.sense_id, g.gloss_id
FROM word w 
INNER JOIN sense s ON s.word_id = w.word_id 
INNER JOIN gloss g ON g.sense_id = s.sense_id 
WHERE g.gloss_string LIKE "%A surname%" 
OR g.gloss_string LIKE "%male given name%" 
OR g.gloss_string LIKE "%female given name%"
OR g.gloss_string LIKE "%patronymic surname%"
OR g.gloss_string LIKE "%habitational surname%"
OR g.gloss_string LIKE "%occupational surname%"
OR g.gloss_string LIKE "%patronymical surname%"
OR g.gloss_string LIKE "%toponymic surname%"
OR g.gloss_string LIKE "%demonymic surname%"
OR g.gloss_string LIKE "%rare surname%"
OR g.gloss_string LIKE "%feminine surname%"
OR g.gloss_string LIKE "%masculine surname%"
OR g.gloss_string LIKE "%geographic surname%"
OR g.gloss_string LIKE "%a common surname%"
OR g.gloss_string LIKE "%Christian surname%"
OR g.gloss_string LIKE "%Spanish surname%"
OR g.gloss_string LIKE "%Russian surname%"
OR g.gloss_string LIKE "%religious surname%"
OR g.gloss_string LIKE "%locative surname%"
OR g.gloss_string LIKE "% (surname) %"
OR g.gloss_string LIKE "% (given name) %"
OR g.gloss_string LIKE "% Arabic given name %"
OR g.gloss_string LIKE "% (Given name %"
""").fetchall()
        for sense_id, gloss_id in name_tuple:
            cur.execute("DELETE FROM sense WHERE sense_id = ?", (sense_id,))
            cur.execute("DELETE FROM gloss WHERE gloss_id = ?", (gloss_id,))

    if delete_words_beginning_or_ending_with_minus:
        cur.execute("DELETE FROM word WHERE word LIKE \"-%\"")  
        cur.execute("DELETE FROM word WHERE word LIKE \"%-\"")  
    if delete_entries_with_space:
        cur.execute("DELETE FROM word WHERE word LIKE \"% %\"")

def link_up_alternative_forms_or_spellings(cur: Cursor):
    #Now add correct glosses to Alternate Form (TODO: Refactor everything)
    alternative_forms = cur.execute("""
SELECT w.word_id, s.sense_id, g.gloss_id, g.gloss_string 
FROM word w 
INNER JOIN sense s ON s.word_id = w.word_id 
INNER JOIN gloss g ON g.sense_id = s.sense_id 
WHERE g.gloss_string LIKE "Alternative form of%"
""").fetchall()

    for word_id, sense_id, gloss_id, gloss_string in alternative_forms:
        standard_form = gloss_string[20:].replace(" (", ";").replace(".", ";").split(";", 1)[0]

        cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) \
SELECT ?, (SELECT w.word_id FROM word w WHERE w.word = ?)", (word_id, standard_form))
        cur.execute("DELETE FROM gloss WHERE gloss_id = ?", (gloss_id,))
        cur.execute("DELETE FROM sense WHERE sense_id = ?", (sense_id,))
    #Add obsolete spelling /form as inflection
    obsolete_forms = cur.execute("""
SELECT w.word_id, s.sense_id, g.gloss_id, g.gloss_string 
FROM word w 
INNER JOIN sense s ON s.word_id = w.word_id 
INNER JOIN gloss g ON g.sense_id = s.sense_id 
WHERE g.gloss_string LIKE "Obsolete form of%"
""").fetchall()

    for word_id, sense_id, gloss_id, gloss_string in obsolete_forms:
        standard_form = gloss_string[17:].replace(" (", ";").replace(".", ";").split(";", 1)[0]
        cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) \
    SELECT ?, (SELECT w.word_id FROM word w WHERE w.word = ?)", (word_id, standard_form))
        cur.execute("DELETE FROM gloss WHERE gloss_id = ?", (gloss_id,))
        cur.execute("DELETE FROM sense WHERE sense_id = ?", (sense_id,))
    obsolete_spelling = cur.execute("""
SELECT w.word_id, s.sense_id, g.gloss_id, g.gloss_string 
FROM word w 
INNER JOIN sense s ON s.word_id = w.word_id 
INNER JOIN gloss g ON g.sense_id = s.sense_id 
WHERE g.gloss_string LIKE "Obsolete spelling of%"
""").fetchall()

    for word_id, sense_id, gloss_id, gloss_string in obsolete_spelling:
        standard_form = gloss_string[21:].replace(" (", ";").replace(".", ";").split(";", 1)[0]
        cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) \
    SELECT ?, (SELECT w.word_id FROM word w WHERE w.word = ?)", (word_id, standard_form))
        cur.execute("DELETE FROM gloss WHERE gloss_id = ?", (gloss_id,))
        cur.execute("DELETE FROM sense WHERE sense_id = ?", (sense_id,))
    alternative_spelling = cur.execute("""
SELECT w.word_id, s.sense_id, g.gloss_id, g.gloss_string 
FROM word w 
INNER JOIN sense s ON s.word_id = w.word_id 
INNER JOIN gloss g ON g.sense_id = s.sense_id 
WHERE g.gloss_string LIKE "Alternative spelling of%"
""").fetchall()

    for word_id, sense_id, gloss_id, gloss_string in alternative_spelling:
        standard_form = gloss_string[24:].replace(" (", ";").replace(".", ";").split(";", 1)[0]
        cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) \
    SELECT ?, (SELECT w.word_id FROM word w WHERE w.word = ?)", (word_id, standard_form))
        cur.execute("DELETE FROM gloss WHERE gloss_id = ?", (gloss_id,))
        cur.execute("DELETE FROM sense WHERE sense_id = ?", (sense_id,))
    archaic_spelling = cur.execute("""
SELECT w.word_id, s.sense_id, g.gloss_id, g.gloss_string 
FROM word w 
INNER JOIN sense s ON s.word_id = w.word_id 
INNER JOIN gloss g ON g.sense_id = s.sense_id 
WHERE g.gloss_string LIKE "Archaic spelling of%"
""").fetchall()

    for word_id, sense_id, gloss_id, gloss_string in archaic_spelling:
        standard_form = gloss_string[20:].replace(" (", ";").replace(".", ";").split(";", 1)[0]
        cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) \
    SELECT ?, (SELECT w.word_id FROM word w WHERE w.word = ?)", (word_id, standard_form))
        cur.execute("DELETE FROM gloss WHERE gloss_id = ?", (gloss_id,))
        cur.execute("DELETE FROM sense WHERE sense_id = ?", (sense_id,))
    pron_spelling = cur.execute("""
SELECT w.word_id, s.sense_id, g.gloss_id, g.gloss_string 
FROM word w 
INNER JOIN sense s ON s.word_id = w.word_id 
INNER JOIN gloss g ON g.sense_id = s.sense_id 
WHERE g.gloss_string LIKE "Pronunciation spelling of%"
""").fetchall()

    for word_id, sense_id, gloss_id, gloss_string in pron_spelling:
        standard_form = gloss_string[26:].replace(" (", ";").replace(".", ";").split(";", 1)[0]
        cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) \
    SELECT ?, (SELECT w.word_id FROM word w WHERE w.word = ?)", (word_id, standard_form))
        cur.execute("DELETE FROM gloss WHERE gloss_id = ?", (gloss_id,))
        cur.execute("DELETE FROM sense WHERE sense_id = ?", (sense_id,))
    #Delete misspelling
    misspelling = cur.execute("""
SELECT w.word_id, s.sense_id, g.gloss_id, g.gloss_string 
FROM word w 
INNER JOIN sense s ON s.word_id = w.word_id 
INNER JOIN gloss g ON g.sense_id = s.sense_id 
WHERE g.gloss_string LIKE "Misspelling of%"
""").fetchall()

    for word_id, sense_id, gloss_id, gloss_string in misspelling:
        cur.execute("DELETE FROM gloss WHERE gloss_id = ?", (gloss_id,))
        cur.execute("DELETE FROM sense WHERE sense_id = ?", (sense_id,))

    rest_spelling = cur.execute(f"""
SELECT w.word_id, s.sense_id, g.gloss_id, g.gloss_string 
FROM word w 
INNER JOIN sense s ON s.word_id = w.word_id 
INNER JOIN gloss g ON g.sense_id = s.sense_id 
WHERE g.gloss_string LIKE "% spelling of %"
""").fetchall()

    for word_id, sense_id, gloss_id, gloss_string in rest_spelling:
        standard_form = gloss_string.split("spelling of ")[1].replace(" (", ";").replace(".", ";").split(";", 1)[0]
        cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) \
    SELECT ?, (SELECT w.word_id FROM word w WHERE w.word = ?)", (word_id, standard_form))
        cur.execute("DELETE FROM gloss WHERE gloss_id = ?", (gloss_id,))
        cur.execute("DELETE FROM sense WHERE sense_id = ?", (sense_id,))
    
    abbreviation = cur.execute(f"""
SELECT w.word_id, s.sense_id, g.gloss_id, g.gloss_string 
FROM word w 
INNER JOIN sense s ON s.word_id = w.word_id 
INNER JOIN gloss g ON g.sense_id = s.sense_id 
WHERE g.gloss_string LIKE "%abbreviation of %"
""").fetchall()

    for word_id, sense_id, gloss_id, gloss_string in abbreviation:
        standard_form = gloss_string.split("bbreviation of ")[1].replace(" (", ";").replace(".", ";").split(";", 1)[0]

        results = cur.execute("SELECT * FROM word WHERE word = ?", (standard_form,)).fetchone()
        if results == None:
            print("No base form found for:")
            print(gloss_string)
        else:
            cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) \
        SELECT ?, (SELECT w.word_id FROM word w WHERE w.word = ?)", (word_id, standard_form))
            cur.execute("DELETE FROM gloss WHERE gloss_id = ?", (gloss_id,))
            cur.execute("DELETE FROM sense WHERE sense_id = ?", (sense_id,))

def directly_link_transitive_base_form_relations(cur: Cursor):
    #Delete the 3 or so entries that for some reason are base forms of themselves (leads to problems)
    cur.execute("""DELETE FROM form_of_word
WHERE form_of_word.word_id = form_of_word.base_word_id""")
    #TODO: Maybe we do not want to delete the intermediate links -> commented out

    #Yeah, this is bugged for "noviecitas"

    transitive_base_of_relation_5 = cur.execute("""
    SELECT w1.word_id, w2.word_id, w3.word_id, w4.word_id, w5.word_id FROM word w1
    JOIN form_of_word fow ON fow.word_id = w1.word_id 
    JOIN word w2 ON fow.base_word_id = w2.word_id 
    JOIN form_of_word fow2 ON fow2.word_id = w2.word_id 
    JOIN word w3 ON fow2.base_word_id = w3.word_id 
    JOIN form_of_word fow3 ON fow3.word_id = w3.word_id 
    JOIN word w4 ON fow3.base_word_id = w4.word_id 
    JOIN form_of_word fow4 ON fow4.word_id = w4.word_id 
    JOIN word w5 ON fow4.base_word_id = w5.word_id 
    WHERE w1.word_id != w3.word_id AND w2.word_id != w4.word_id 
    AND w1.word != "noviecitas"
    """).fetchall()

    for word1_id, word2_id, word3_id, word4_id, word5_id in transitive_base_of_relation_5:
        cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) VALUES (?, ?)", (word1_id, word5_id))
        #cur.execute("DELETE FROM form_of_word WHERE form_of_word.word_id = ? AND form_of_word.base_word_id = ?", (word1_id, word2_id))
#This is slow, but whatever
    transitive_base_of_relation_4 = cur.execute("""
SELECT w1.word_id, w2.word_id, w3.word_id, w4.word_id FROM word w1
JOIN form_of_word fow ON fow.word_id = w1.word_id 
JOIN word w2 ON fow.base_word_id = w2.word_id 
JOIN form_of_word fow2 ON fow2.word_id = w2.word_id 
JOIN word w3 ON fow2.base_word_id = w3.word_id 
JOIN form_of_word fow3 ON fow3.word_id = w3.word_id 
JOIN word w4 ON fow3.base_word_id = w4.word_id 
WHERE w1.word_id != w3.word_id
    """).fetchall()

    for word1_id, word2_id, word3_id, word4_id in transitive_base_of_relation_4:
        cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) VALUES (?, ?)", (word1_id, word4_id))
        #cur.execute("DELETE FROM form_of_word WHERE form_of_word.word_id = ? AND form_of_word.base_word_id = ?", (word1_id, word2_id))
    #Now break up base_of relations that go like word1 -> word2 -> word3
    transitive_base_of_relation_3 = cur.execute("""
    SELECT w1.word_id, w2.word_id, w3.word_id FROM word w1
JOIN form_of_word fow ON fow.word_id = w1.word_id 
JOIN word w2 ON fow.base_word_id = w2.word_id 
JOIN form_of_word fow2 ON fow2.word_id = w2.word_id 
JOIN word w3 ON fow2.base_word_id = w3.word_id 
    """).fetchall()

    for word1_id, word2_id, word3_id in transitive_base_of_relation_3:
        if word1_id != word3_id:
            cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) VALUES (?, ?)", (word1_id, word3_id))
        #cur.execute("DELETE FROM form_of_word WHERE form_of_word.word_id = ? AND form_of_word.base_word_id = ?", (word1_id, word2_id))
    #Now delete entries that don't have senses -> There would be currently many basic words like fue vieses or visto in this that 
    #are caused by a bug in Wiktextract if I hadn't implemented a workaround
    cur.execute("""DELETE FROM word 
WHERE word.word_id NOT IN (SELECT sense.word_id FROM sense) AND word.word_id NOT IN (SELECT form_of_word.word_id FROM form_of_word)
""")

def create_database(output_db_path: str, wiktextract_json_file: str, language: str):
    try:
        os.remove(output_db_path)
    except:
        pass
    with open('create_databases/create_db_tables_spanish.sql', 'r') as sql_file:
        sql_script = sql_file.read()

    con = sqlite3.connect(output_db_path)

    cur = con.cursor()
    cur.executescript(sql_script)
    con.commit()

    with open(wiktextract_json_file, "r", encoding="utf-8") as f:
                                    #word_id, base_word_string
        form_of_words_to_add_later: "list[tuple(int, str)]" = []
        for line in f:

            obj = json.loads(line)

            word_pos = obj["pos"]
            word_word = obj["word"]

            cur.execute("INSERT INTO word (pos, word) VALUES (?, ?)",
                (word_pos, word_word))
            word_id = cur.lastrowid


            for sense in obj["senses"]:
                if "form_of" in sense:
                    for base_word in sense["form_of"]:
                        #TODO: This introduces some errors, but fixes more important ones
                        if base_word["word"][-1] == "." and base_word["word"][-2].islower():
                            base_word["word"] = base_word["word"][:-1]
                        form_of_words_to_add_later.append((word_id, base_word["word"]))
                    #todo: fix for glosses that aren't the base word (pretty rare case)
                else:
                    cur.execute("INSERT INTO sense (word_id) VALUES (?)", (word_id,))
                    sense_id = cur.lastrowid
                    try:
                        for gloss in sense["glosses"]:
                            gloss_sense_id = sense_id
                            gloss_string = gloss
                            cur.execute("INSERT INTO gloss (sense_id, gloss_string) VALUES(?, ?)", (gloss_sense_id, gloss_string))
                    except:
                        pass
                    
        con.commit()
            #add form of words after all data has been inserted

        create_indices(cur)

        con.commit()

        t0 = time.time()

        insert_base_linkages(form_of_words_to_add_later, cur)

        t1 = time.time()
        print(t1 - t0)

        if language == "English":
            #Loading times are unfortunately a bit longer
            #So it might be a good idea to filter out more, but it hard to find out what
            delete_unneeded_entries(cur, delete_entries_with_space=True)
        elif language == "Arabic":
            delete_unneeded_entries(cur, delete_words_without_chars=False)
        else:
            delete_unneeded_entries(cur)

        if language == "Spanish":
            add_linkages_to_spanish_compound_words(cur)
        elif language == "Italian":
            add_linkages_to_spanish_compound_words(cur)

        link_up_alternative_forms_or_spellings(cur)

        directly_link_transitive_base_form_relations(cur)

    con.commit()
    con.close()

