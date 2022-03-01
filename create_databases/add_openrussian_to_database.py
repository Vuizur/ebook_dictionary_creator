from email.mime import base
import sqlite3
#import create_database
from create_databases.create_database_russian import add_inflection_to_db

from helper_functions import begins_with_star, contains_apostrophes_or_yo, convert_ap_accent_to_real, remove_accent_if_only_one_syllable, remove_apostrophes, remove_parantheses, remove_yo, unaccentify


#def convert_ap_accent_to_real(word: str) -> str:
#    res = ""
#    for char in word:
#        if char != "'":
#            res += char
#        else:
#            res += u'\u0301'
#    return res
#
#translation_table_ap = {ord("'"): None}
#def remove_apostrophes(word: str) -> str:
#    return word.translate(translation_table_ap)
#
#def remove_yo(word: str) -> str:
#    res = ""
#    for char in word:
#        if char != "ё":
#            res += char
#        else:
#            res += "е"
#    return res
#
#def contains_apostrophes_or_yo(word: str) -> bool:
#    for char in word:
#        if char == "'" or char == "ё":
#            return True
#    return False
#
#def begins_with_star(word: str) -> bool:
#    """Returns true if the word should be ignored"""
#    return len(word) == 0 or word == None or word[0] == "*"
#
#def remove_parantheses(word: str) -> bool:
#    return word.replace("(", "").replace(")", "")

def output_difference_of_word_list(openrussian_wordlist: list[str], database_path):
    con = sqlite3.connect(database_path)
    cur = con.cursor()
    words = cur.execute("SELECT word FROM word").fetchall()
    OR_wordlist = set()
    for word in openrussian_wordlist:
        OR_wordlist.add(remove_apostrophes(word))

    wiktionary_wordlist = set()
    for word in words:
        wiktionary_wordlist.add(word[0])

    stuff_not_in_wiktionary = OR_wordlist - wiktionary_wordlist
    stuff_not_in_OpenRussian = wiktionary_wordlist - OR_wordlist
    with open("vocab_differences.txt", "w+", encoding="utf-8") as output:
        output.write("######## VOCABULARY NOT IN WIKTIONARY  ##########")
        for wrd in stuff_not_in_wiktionary:
            output.write(wrd + "\n")
        output.write("\n\n\n####### VOCABULARY NOT IN OpenRUSSIAN ###########\n\n")
        for wrd in stuff_not_in_OpenRussian:    
            output.write(wrd + "\n")

class BaseWord():
    base_word: str
    word_id: str
    pos: str
    inflections: set[str]
    definitions: list[tuple[str, str]]
    """List of tuples of language (en, de) and definition string"""

    def __init__(self) -> None:
        self.inflections = set()
        self.definitions = []

    def process_all_data(self) -> None:
        """This removes commas and strange symbols"""
        
        inflections_fixed = set()
        self.base_word = remove_accent_if_only_one_syllable(convert_ap_accent_to_real(remove_parantheses(self.base_word)))
        #Split up words
        for inflection in self.inflections:
            if ";" in inflection or "," in inflection:
                split_words = inflection.replace(",", ";").split(";")
                split_words = list(map(str.strip, split_words))
                inflections_fixed.update(split_words)
            else:
                inflections_fixed.add(inflection)
        inflections_final = set()
        for inflection in inflections_fixed:
            if begins_with_star(inflection):
                continue
            else:
                inflections_final.add(remove_accent_if_only_one_syllable(convert_ap_accent_to_real(remove_parantheses(inflection))))
        self.inflections = inflections_final

    def add_to_database(self, cur: sqlite3.Cursor):

        #Add base word if not exists
        unaccentified_base_word = unaccentify(self.base_word)
        lowercase = unaccentified_base_word.lower()
        without_yo = remove_yo(lowercase)
        unclear_pos = False
        if self.pos == "other" or self.pos == None:
            unclear_pos = True
        
        sql_str = "SELECT w.word_id FROM word w WHERE w.canonical_form = ? OR w.alternative_canonical_form = ?"
        if not unclear_pos:
            sql_str += " AND w.pos = ?"
        already_there_id = cur.execute(sql_str, (self.base_word, self.base_word, self.pos)).fetchone()
        if already_there_id == None:
            cur.execute("INSERT INTO word (word, canonical_form, pos, word_lowercase, word_lower_and_without_yo) \
            VALUES (?, ?, ?, ?, ?)", (unaccentified_base_word, self.base_word, self.pos, lowercase, without_yo))
            word_id = cur.lastrowid
            cur.execute("INSERT INTO sense (word_id) VALUES (?)", (word_id,))
            sense_id = cur.lastrowid
            for lang, def_str in self.definitions:
                cur.execute("INSERT INTO gloss (sense_id, gloss_string, gloss_lang, gloss_source) VALUES(?, ?, ?, ?)", (sense_id, def_str, lang, "op"))
            for inflection in self.inflections:
                add_inflection_to_db(cur, inflection, self.pos, word_id, [])   
       

def get_definitions(cur: sqlite3.Cursor, word_id) -> list[tuple[str, str]]:
    translations_list = []
    translations = cur.execute("SELECT lang, tl FROM translations WHERE word_id = ?", (word_id,)).fetchall()
    for lang, tl in translations:
        translations_list.append((lang, tl))
    return translations_list

def add_openrussian_to_db_with_linkages(database_path, openrussian_database_path):
    openrussian = sqlite3.connect(openrussian_database_path)
    base_words: list[BaseWord] = []
    print("Transform adjectives")
    #Add adjectives
    words = openrussian.execute("""
SELECT w.id, w.accented, a.comparative, a.superlative, a.short_n, a.short_f, a.short_pl, d.nom, d.gen, d.dat, d.acc, d.inst, d.prep FROM words w
JOIN adjectives a ON w.id = a.word_id
JOIN declensions d ON d.word_id = w.id
""")#.fetchall()
    current_w_id = None
    base_word = None
    chunk_size = 200
    count = 0
    while True:
        words_fetched = words.fetchmany(chunk_size) 
        if not words_fetched:
            break
        else:
            for w_id, accented, comparative, superlative, short_n, short_f, short_pl, d_nom, d_gen, d_dat, d_acc, d_inst, d_prep in words_fetched:
                count += 1
                if current_w_id != w_id:
                    if base_word != None:
                        base_words.append(base_word)
                    base_word = BaseWord()
                    base_word.pos = "adj"
                    base_word.base_word = accented
                    base_word.definitions = get_definitions(openrussian, w_id)
                    base_word.inflections.update([comparative, superlative, short_n, short_f, short_pl])
                    current_w_id = w_id
                base_word.inflections.update([d_nom, d_gen, d_dat, d_acc, d_inst, d_prep])
            base_words.append(base_word)
    print(str(count) + " adjectives inserted")
    print("Transform verbs")

    #Add verbs
    verbs = openrussian.execute("""
    SELECT w.id, w.accented, v.imperative_sg, v.imperative_pl, v.past_m, v.past_f, v.past_n, v.past_pl, c.sg1, c.sg1, c.sg3, c.pl1, c.pl2, c.pl3 FROM words w
    JOIN verbs v ON w.id = v.word_id    
    JOIN conjugations c ON c.word_id = w.id 
    """).fetchall()
    for w_id, accented, imperative_sg, imperative_pl, past_m, past_f, past_n, past_pl, sg1, sg2, sg3, pl1, pl2, pl3 in verbs:
        base_word = BaseWord()
        base_word.pos = "verb"
        base_word.base_word = accented
        base_word.definitions = get_definitions(openrussian, w_id)
        base_word.inflections.update([imperative_sg, imperative_pl, past_m, past_f, past_n, past_pl, sg1, sg2, sg3, pl1, pl2, pl3])
        base_words.append(base_word)

    print("Transform nouns and rest")
    #Add nouns and rest
    rest = openrussian.execute("""
    SELECT w.id, w.type, w.accented, d.nom, d.gen, d.dat, d.acc, d.inst, d.prep FROM words w
JOIN declensions d ON d.word_id = w.id WHERE w.type != "verb" AND w.type != "adjective"
""").fetchall()

    current_w_id = None
    base_word = None
    for w_id, w_type, accented, d_nom, d_gen, d_dat, d_acc, d_inst, d_prep in rest:
        if w_type == "adverb":
            w_type = "adv"
        if current_w_id != w_id:
            if base_word != None:
                base_words.append(base_word)
            base_word = BaseWord()
            base_word.pos = w_type
            base_word.base_word = accented
            base_word.definitions = get_definitions(openrussian, w_id)
            current_w_id = w_id
        base_word.inflections.update([d_nom, d_gen, d_dat, d_acc, d_inst, d_prep])
    base_words.append(base_word)

    print("Add everything to database")

    wikt_db = sqlite3.connect(database_path)
    wikt_cur = wikt_db.cursor()

    #Add to database
    for base_word in base_words:
            base_word.process_all_data()
            base_word.add_to_database(wikt_cur)
    wikt_db.commit()
    wikt_cur.close()
    wikt_db.close()

def add_openrussian_to_db(database_path, openrussian_database_path):

    con = sqlite3.connect(database_path)
    openrussian = sqlite3.connect(openrussian_database_path)
    
    words_to_add: list[str] = []
    adjectives = openrussian.execute("SELECT comparative, superlative, short_m, short_f, short_n, short_pl from adjectives").fetchall()
    for comparative, superlative, short_m, short_f, short_n, short_pl in adjectives:
        words_to_add.extend([comparative, superlative, short_m, short_f, short_n, short_pl])
    conjugations = openrussian.execute("SELECT sg1, sg1, sg3, pl1, pl2, pl3 FROM conjugations").fetchall()
    for sg1, sg2, sg3, pl1, pl2, pl3 in conjugations:
        words_to_add.extend([sg1, sg2, sg3, pl1, pl2, pl3])
    declensions = openrussian.execute("SELECT nom, gen, dat, acc, inst, prep FROM declensions").fetchall()
    for nom, gen, dat, acc, inst, prep in declensions:
        words_to_add.extend([nom, gen, dat, acc, inst, prep])
    verbs = openrussian.execute("SELECT imperative_sg, imperative_pl, past_m, past_f, past_n, past_pl FROM verbs").fetchall()
    for imperative_sg, imperative_pl, past_m, past_f, past_n, past_pl in verbs:
        words_to_add.extend([imperative_sg, imperative_pl, past_m, past_f, past_n, past_pl])
    words = openrussian.execute("SELECT accented from words").fetchall()
    for accented in words:
        words_to_add.extend([accented[0]])    
    words_to_add = [word for word in words_to_add if (word != None) and contains_apostrophes_or_yo(word) and "[" not in word]

    words_split_up = []
    for word in words_to_add:
        if ";" in word or "," in word:
            split_words = word.replace(",", ";").split(";")
            split_words = list(map(str.strip, split_words))
            words_split_up.extend(split_words)
        else:
            words_split_up.append(word)
    words_split_up = [word for word in words_split_up if " " not in word]
    words_split_up = list(dict.fromkeys(words_split_up))

    #output_difference_of_word_list(words_split_up)
    #quit()

    for w in words_split_up:
        if begins_with_star(w):
            continue #this means that the word is unused -> we don't need it
        w = remove_parantheses(w)
        word_without_apostrophes = remove_apostrophes(w)
        word_accented = remove_accent_if_only_one_syllable(convert_ap_accent_to_real(w))
        word_lowercase = word_without_apostrophes.lower()
        word_lower_and_without_yo = remove_yo(word_lowercase)
        
        already_there = con.execute("SELECT word FROM word w WHERE w.canonical_form = ? OR w.alternative_canonical_form = ?",
            (word_accented, word_accented)).fetchone()

        if already_there == None:
            con.execute("INSERT INTO word (word, canonical_form, word_lowercase, word_lower_and_without_yo) VALUES (?, ?, ?, ?)",
                (word_without_apostrophes, word_accented, word_lowercase, word_lower_and_without_yo)
            )
            #print(w)
    con.commit()
    con.close()