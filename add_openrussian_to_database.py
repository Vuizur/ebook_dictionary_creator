import sqlite3

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

def add_openrussian_to_db():
    con = sqlite3.connect("words4.db")
    openrussian = sqlite3.connect("openrussian.db")
    
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
    for w in words_split_up:
        word_without_apostrophes = remove_apostrophes(w)
        word_accented = convert_ap_accent_to_real(w)
        word_lowercase = word_without_apostrophes.lower()
        word_lower_and_without_yo = remove_yo(word_lowercase)
        already_there = con.execute("SELECT word FROM word w WHERE w.canonical_form = ?",
            (word_accented,)).fetchone()
        if already_there == None:
            con.execute("INSERT INTO word (word, canonical_form, word_lowercase, word_lower_and_without_yo) VALUES (?, ?, ?, ?)",
                (word_without_apostrophes, word_accented, word_lowercase, word_lower_and_without_yo)
            )
            #print(w)
    con.commit()
    con.close()
add_openrussian_to_db()
