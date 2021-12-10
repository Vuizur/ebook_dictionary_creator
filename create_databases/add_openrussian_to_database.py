import sqlite3

from helper_functions import remove_accent_if_only_one_syllable

DATABASE_NAME = "russian_dict.db"

def convert_ap_accent_to_real(word: str) -> str:
    res = ""
    for char in word:
        if char != "'":
            res += char
        else:
            res += u'\u0301'
    return res

translation_table_ap = {ord("'"): None}
def remove_apostrophes(word: str) -> str:
    return word.translate(translation_table_ap)

def remove_yo(word: str) -> str:
    res = ""
    for char in word:
        if char != "ё":
            res += char
        else:
            res += "е"
    return res

def contains_apostrophes_or_yo(word: str) -> bool:
    for char in word:
        if char == "'" or char == "ё":
            return True
    return False

def begins_with_star(word: str) -> bool:
    """Returns true if the word should be ignored"""
    return len(word) == 0 or word == None or word[0] == "*"

def remove_parantheses(word: str) -> bool:
    return word.replace("(", "").replace(")", "")

def output_difference_of_word_list(openrussian_wordlist: list[str]):
    con = sqlite3.connect(DATABASE_NAME)
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
    
def add_openrussian_to_db():

    con = sqlite3.connect(DATABASE_NAME)
    openrussian = sqlite3.connect("openrussian_csv_new.db")
    
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

if __name__ == "__main__":
    add_openrussian_to_db()

#add_openrussian_to_db()