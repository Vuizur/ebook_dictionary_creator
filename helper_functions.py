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

def has_cyrillic_letters(s: str):
    m = re.findall(r'[А-я]+', s)
    return m != []

#Wiktionary data is a bit buggy
def remove_weird_characters_for_alternative_canonical(s: str):
    return(s.replace("^*", ""))

gloss_string = "Alternative spelling of Baréin"
standard_form = gloss_string[24:].replace(" (", ";").split(";", 1)[0]

print(standard_form)
