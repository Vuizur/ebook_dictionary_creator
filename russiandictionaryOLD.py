import json

import unicodedata

class RuDictionary:

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


    def unaccentify(self, s):
        source = unicodedata.normalize('NFKC', s)
        for old, new in self.ACCENT_MAPPING.items():
            source = source.replace(old, new)
        return source

    def __init__(self):
        with open("real-json-dict.json", "r", encoding="utf-8") as dict_file:
            self.dict_json = json.load(dict_file)

    def look_for_word_json(self, word: str, dict_json):
        etymologies = []
        #set of base forms to prevent duplicates
        base_forms = set()
        for obj in dict_json:
            if obj["word"] == word:
                for sense in obj["senses"]:
                    if "form_of" in sense:
                        base_form = obj["senses"][0]["form_of"][0]["word"]
                        base_form = self.unaccentify(base_form)
                        base_forms.add(base_form)
                    else:
                        glosses = []
                        for gloss in sense["glosses"]:
                            glosses.append(gloss)
                        #does this work for all forms?
                        base_form = obj["forms"][0]["form"]
                        etymologies.append((base_form, glosses))
        #look for base forms
        for base_form in base_forms:
            base_form_definitions = self.look_for_word_json(base_form, dict_json)
            etymologies = etymologies + base_form_definitions
        return etymologies

    def get_entries(self, word):
        return self.look_for_word_json(word, self.dict_json)

rdict = RuDictionary()

print(rdict.get_entries("гори"))
print(rdict.get_entries("белой"))
    #res = look_for_word(word_to_search, dict_json)
        #print(res)