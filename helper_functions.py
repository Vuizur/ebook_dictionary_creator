import unicodedata
import re

#Wiktionary data is a bit buggy
def remove_weird_characters_for_alternative_canonical(s: str):
    return(s.replace("^*", ""))

def begins_with_star(word: str) -> bool:
    """Returns true if the word should be ignored"""
    return len(word) == 0 or word == None or word[0] == "*"

def remove_parantheses(word: str) -> bool:
    return word.replace("(", "").replace(")", "")

def contains_apostrophes_or_yo(word: str) -> bool:
    for char in word:
        if char == "'" or char == "ё":
            return True
    return False