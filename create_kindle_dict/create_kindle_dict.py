from pyglossary import Glossary
import sqlite3
from unidecode import unidecode
import collections





# To get the kindle dictionary creation to run, you need to replace following function/constant in the pyglossary package
# (ebook-mobi.py)
GROUP_XHTML_WORD_DEFINITION_TEMPLATE = """<idx:entry \
scriptable="yes"{spellcheck_str}>
<idx:orth{headword_hide}>{headword_html}{infl}
</idx:orth>
<br/>{definition}
</idx:entry>
<hr/>"""

def format_group_content(self, word: "List[str]", defi: str) -> str:
    hide_word_index = self._hide_word_index
    html_headword = None
    if word[0][:9] == "HTML_HEAD":
        html_headword = word[0][9:]
        word.pop(0)

    if hide_word_index:
        html_headword = ''
    if len(word) == 1:
        infl = ''
        mainword = word[0]
    else:
        mainword, *variants = word
        iforms_list = []
        for variant in variants:
            iforms_list.append(self.GROUP_XHTML_WORD_IFORM_TEMPLATE.format(
                inflword=variant,
                exact_str=' exact="yes"' if self._exact else '',
            ))
        infl = '\n' + \
            self.GROUP_XHTML_WORD_INFL_TEMPLATE.format(
                iforms_str="\n".join(iforms_list))

    headword = self.escape_if_needed(mainword)

    defi = self.escape_if_needed(defi)

    group_content = self.GROUP_XHTML_WORD_DEFINITION_TEMPLATE.format(
        spellcheck_str=' spell="yes"' if self._spellcheck else '',
        headword_html=f'\n{headword}' if html_headword == None else f'\n{html_headword}',
        headword_hide=f' value="{headword}"' if not html_headword == None else '',
        definition=defi,
        infl=infl,
    )
    return group_content


def create_kindle_dict(source_database_path: str, input_language: str, output_language: str, output_path: str, author: str,
                       title: str, try_to_fix_kindle_lookup_stupidity=False):
    """Creates a kindle dictionary. The try_to_fix_kindle_lookup_stupidity is much slower, but vastly improves the lookup
    of words that are not recognized by default due to the buggy algorithm that does not look at inflections if a fitting
    base word exists
    """
    Glossary.init()
    glos = Glossary()

    defiFormat = "h"

    con = sqlite3.connect(source_database_path)
    cur = con.cursor()
    print("Getting base forms")
    base_forms = cur.execute("""SELECT word_id, word FROM word 
WHERE word.word_id IN (SELECT sense.word_id FROM sense) GROUP BY word
""").fetchall()

    # this serves to check overlappings with base forms
    base_forms_unidecoded = set()
    for base_form in base_forms:
        base_forms_unidecoded.add(unidecode(base_form[1]).lower())

    inflection_num = 0
    counter = 0
    print("Iterating through base forms:")

    if try_to_fix_kindle_lookup_stupidity:
        # This is needed to detect collisions between inflections

        all_inflections = []
        for word_id, canonical_form in base_forms:
            inflections = cur.execute("""SELECT w1.word FROM word w1
JOIN form_of_word fow ON fow.word_id = w1.word_id 
JOIN word w2 ON w2.word_id = fow.base_word_id 
WHERE w2.word = ?""", (canonical_form,)).fetchall()
            word_inflections = []
            for inflection in inflections:
                word_inflections.append(unidecode(inflection[0].lower()))
            # Necessary because of too much form_of_word linkages
            all_inflections.extend(list(set(word_inflections)))

        print("Count all elements: ")
        inflection_counts = collections.Counter(all_inflections)
        print("Elements counted")

    for word_id, canonical_form in base_forms:
        counter = counter + 1

        glosses = cur.execute("""SELECT g.gloss_string
FROM word w 
INNER JOIN sense s ON s.word_id = w.word_id 
INNER JOIN gloss g ON g.sense_id = s.sense_id 
WHERE w.word = ?""", (canonical_form,)).fetchall()

        glosses_list = []
        for gloss in glosses:
            if gloss[0] == None:  # This appears to happen for some reason
                continue
            glosses_list.append(gloss[0].strip())
        glosses_list = list(dict.fromkeys(glosses_list))
        glosshtml = ""
        for gloss in glosses_list:
            glosshtml += "<p>" + gloss + "</p>"

        # get inflections
        inflections = cur.execute("""SELECT w1.word FROM word w1
JOIN form_of_word fow ON fow.word_id = w1.word_id 
JOIN word w2 ON w2.word_id = fow.base_word_id 
WHERE w2.word = ?""", (canonical_form,)).fetchall()

        infl_list = []
        for inflection in inflections:
            # This seeks to avoid double entries like aquella which links to aquélla and both have the same glosses and are
            # found both due to the stupid kindle algorithm
            if try_to_fix_kindle_lookup_stupidity and unidecode(canonical_form) != unidecode(inflection[0]):
                infl_list.append(inflection[0])
        # This has to do with a bug in the linkages that causes words to be doubly linked
        infl_list = list(set(infl_list))
        already_separated_unidecoded_inflections = set()

        rest_inflections = []
        for inflection in infl_list:
            unidecoded_inflection = unidecode(inflection)
            if try_to_fix_kindle_lookup_stupidity and (not unidecoded_inflection in already_separated_unidecoded_inflections) \
                    and ((unidecoded_inflection.lower() in base_forms_unidecoded) or (inflection_counts[inflection] > 1)):
                # these forms will otherwise not be found by the stupid algorithm
                pgl_list = ["HTML_HEAD<b>" +
                            canonical_form + "</b>", inflection]
                glos.addEntryObj(glos.newEntry(
                    pgl_list, glosshtml, defiFormat))
                already_separated_unidecoded_inflections.add(
                    unidecoded_inflection)
            else:
                rest_inflections.append(inflection)

        inflection_num += len(infl_list)

        all_forms = ["HTML_HEAD<b>" + canonical_form + "</b>", canonical_form]
        all_forms.extend(rest_inflections)
        glos.addEntryObj(glos.newEntry(all_forms, glosshtml, defiFormat))

        if counter % 2000 == 0:
            print(str(counter) + " words")
    print("Creating dictionary")
    glos.setInfo("title", title)
    glos.setInfo("author", author)
    glos.sourceLangName = input_language
    glos.targetLangName = output_language
    print("Writing dictionary")
    glos.write(output_path, format="Mobi", keep=True, exact=True, spellcheck=False,
               kindlegen_path="C:/Users/hanne/AppData/Local/Amazon/Kindle Previewer 3/lib/fc/bin/kindlegen.exe")
    #glos.write("spanish_dictionary.kobo", format="Kobo")
    print(str(len(base_forms)) + " base forms")
    print(str(inflection_num) + " inflections")
    cur.close()
    con.close()
