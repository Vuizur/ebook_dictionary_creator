import sqlite3

from ebook_dictionary_creator.database_creator.helper_functions import contains_stress, has_at_most_one_syllable, has_cyrillic_letters
def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)
    
def word_is_improperly_stressed(word: str):
    if " " in word:
        words = word.split(" ")
        for wrd in words:
            if word_is_improperly_stressed(wrd):
                return True
        return False
    if len(word) > 0 and "-" != word[0] and "-" != word[-1] and has_cyrillic_letters(word) and not has_at_most_one_syllable(word)\
        and not contains_stress(word) and not "ѣ̈" in word and word != word.upper() and not has_numbers(word):
        return True

def find_words_without_stress(database_path):
    con = sqlite3.connect(database_path)
    cur = con.cursor()
    words = cur.execute("SELECT canonical_form FROM word ORDER BY word_id").fetchall()
    words = list(set(words))
    with open("words_without_canonical_form.txt", "w", encoding="utf-8") as f:
        for (word,) in words:
            if word_is_improperly_stressed(word):
                f.write(word + "\n")
