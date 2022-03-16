import unicodedata
import re

ACCENT_MAPPING = {
        '́': '',
        '̀': '',
        'а́': 'а',
        'а̀': 'а',
        'е́': 'е',
        'ѐ': 'е',
        'и́': 'и',
        'ѝ': 'и',
        'о́': 'о',
        'о̀': 'о',
        'у́': 'у',
        'у̀': 'у',
        'ы́': 'ы',
        'ы̀': 'ы',
        'э́': 'э',
        'э̀': 'э',
        'ю́': 'ю',
        '̀ю': 'ю',
        'я́́': 'я',
        'я̀': 'я',
    }

ACCENT_MAPPING = {unicodedata.normalize('NFKC', i): j for i, j in ACCENT_MAPPING.items()}

def unaccentify( s):
    source = unicodedata.normalize('NFKC', s)
    for old, new in ACCENT_MAPPING.items():
        source = source.replace(old, new)
    return source

def remove_accent_if_only_one_syllable(s: str):
    s_unaccented = unaccentify(s)
    s_unaccented_lower = s_unaccented.lower()
    vowels = 0
    for char in s_unaccented_lower:
        if char in "аоэуыяеюи":
            vowels += 1
    if vowels <= 1:
        return s_unaccented
    else:
        return s
def has_at_most_one_syllable(s: str):
    s_unaccented = unaccentify(s)
    s_unaccented_lower = s_unaccented.lower()
    vowels = 0
    for char in s_unaccented_lower:
        if char in "аоэуыяеюи":
            vowels += 1
    return vowels <= 1
    

def has_cyrillic_letters(s: str):
    m = re.findall(r'[А-я]+', s)
    return m != []

#Wiktionary data is a bit buggy
def remove_weird_characters_for_alternative_canonical(s: str):
    return(s.replace("^*", ""))

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

def contains_stress(word: str) -> bool:
    for char in word.lower():
        if char == "\u0301" or char == "ё":
            return True
    return False