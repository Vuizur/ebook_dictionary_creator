import json
import sqlite3
import time
import os


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


#engine = create_engine('sqlite:///words.db')
#sessionmake = sessionmaker(bind=engine)
#session: Session = sessionmake()
try:
    os.remove("spanish_dict.db")
except:
    pass
with open('create_db_tables_spanish.sql', 'r') as sql_file:
    sql_script = sql_file.read()

con = sqlite3.connect('spanish_dict.db')
cur = con.cursor()
cur.executescript(sql_script)
#cur.execute("PRAGMA journal_mode = WAL;")
con.commit()


with open("spanish-dict-utf8.json", "r", encoding="utf-8") as f:
                                #word_id, base_word_string
    form_of_words_to_add_later: "list[tuple(int, str)]" = []
    for line in f:

        dict_json = json.loads(line)

        #iterate through all hundreds of thousands objects
        #form_col = None
        #form_string = None
        pos = None
        #form_dict = {
        #"canonical_form": None,
        #"romanized_form": None,
        #"genitive_form": None,
        #"adjective_form": None,
        #"nominative_plural_form": None,
        #"genitive_plural_form": None
        #}
        word = None
        lang_code = None

        obj = dict_json
        word_pos = obj["pos"]
        word_lang_code = obj["lang_code"]
        word_word = obj["word"]

        cur.execute("INSERT INTO word (pos, word, lang_code) VALUES (?, ?, ?)",
            (word_pos, word_word, word_lang_code))
        word_id = cur.lastrowid
        

        for sense in obj["senses"]:
            if "form_of" in sense:
                for base_word in sense["form_of"]:
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

    #with open("forms_to_add_later.json", 'w', encoding="utf-8") as f:
    ## indent=2 is not needed but makes the file human-readable
    #    json.dump(form_of_words_to_add_later, f, indent=2, ensure_ascii=False) 

    cur.execute("CREATE INDEX word_word_index ON word(word);")
    cur.execute("CREATE INDEX sense_word_id_index ON sense(word_id);")
    cur.execute("CREATE INDEX gloss_sense_id_index ON gloss(sense_id);")


    con.commit()
    records = []
    t0 = time.time()

    for index in range(0, len(form_of_words_to_add_later), 10000):

    #for form_of_entry in form_of_words_to_add_later:
        for word_id, base_word in form_of_words_to_add_later[index: index+10000]:

            cur.execute("INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) \
SELECT ?, (SELECT w.word_id FROM word w WHERE w.word = ?)", (word_id, base_word))


    t1 = time.time()
    print(t1 - t0)

con.commit()
con.close()

