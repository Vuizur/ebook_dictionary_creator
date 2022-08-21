from pyglossary import Glossary
import sqlite3
from unidecode import unidecode
import collections

from ebook_dictionary_creator.e_dictionary_creator.tatoeba_augmentation import get_word_and_html_for_all_words_not_in_word_list


def get_html(POS: str, definitions: list[str]):
    """
    Returns the html for the given definitions and POS.
    """

    # Remove duplicates from the definitions, keep the order
    definitions = list(dict.fromkeys(definitions))

    # Write the pos in cursive to the html
    html = "<i>" + POS + "</i><br>"
    # Write the definitions to the html using an ordered list
    html += "<ol>"
    for definition in definitions:
        html += "<li>" + definition + "</li>"
    html += "</ol>"

    return html

Gloss = collections.namedtuple("Gloss", ["pos", "definition"])

def get_html_from_gloss_list(gloss_list: list[Gloss]):
    """
    Returns the html for the given gloss list.
    """
    html = ""
    # Group the glosses by pos
    gloss_by_pos = {}
    for gloss in gloss_list:
        if gloss.pos not in gloss_by_pos:
            gloss_by_pos[gloss.pos] = []
        gloss_by_pos[gloss.pos].append(gloss.definition)
    
    html_parts: list[str] = []

    for pos in gloss_by_pos:
        html_parts.append(get_html(pos, gloss_by_pos[pos]))
        
    return "<br>".join(html_parts)
   

def create_kindle_dict(source_database_path: str, input_language: str, output_language: str, output_path: str, author: str,
                       title: str, kindlegen_path, try_to_fix_kindle_lookup_stupidity=False, tatoeba_path=None):
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

        glosses = cur.execute("""SELECT g.gloss_string, w.pos
FROM word w 
INNER JOIN sense s ON s.word_id = w.word_id 
INNER JOIN gloss g ON g.sense_id = s.sense_id 
WHERE w.word = ?""", (canonical_form,)).fetchall()
      
        # Cast glosses to a list of Gloss namedtuples
        glosses_list: list[Gloss] = []
        for gloss in glosses:
            if gloss[0] == None:
                continue
            glosses_list.append(Gloss(gloss[1], gloss[0].strip()))

        glosshtml = get_html_from_gloss_list(glosses_list)

        # get inflections
        inflections = cur.execute("""SELECT w1.word FROM word w1
JOIN form_of_word fow ON fow.word_id = w1.word_id 
JOIN word w2 ON w2.word_id = fow.base_word_id 
WHERE w2.word = ?""", (canonical_form,)).fetchall()

        infl_list = []
        for inflection in inflections:
            # This seeks to avoid double entries like aquella which links to aquélla and both have the same glosses and are
            # found both due to the stupid kindle algorithm
            if try_to_fix_kindle_lookup_stupidity:
                if unidecode(canonical_form) != unidecode(inflection[0]):
                    infl_list.append(inflection[0])
            else:
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

        # Augment with data froma Tatoeba:
        
        if counter % 2000 == 0:
         print(str(counter) + " words")
    if tatoeba_path != None:
        existing_words = cur.execute("""SELECT w.word FROM word w""").fetchall()
        existing_words = [word[0] for word in existing_words]
        tatoeba_words = get_word_and_html_for_all_words_not_in_word_list(existing_words, "Sentence pairs in Czech-English - 2022-06-15.tsv")
        for word, html in tatoeba_words.items():
            glos.addEntryObj(glos.newEntry(
               ["HTML_HEAD<b>" + word + "</b>", word], html, defiFormat))

 
    print("Creating dictionary")
    glos.setInfo("title", title)
    glos.setInfo("author", author)
    glos.sourceLangName = input_language
    glos.targetLangName = output_language
    print("Writing dictionary")
    glos.write(output_path, format="Mobi", keep=True, exact=True, spellcheck=False,
               kindlegen_path=kindlegen_path)
    #glos.write("spanish_dictionary.kobo", format="Kobo")
    print(str(len(base_forms)) + " base forms")
    print(str(inflection_num) + " inflections")
    cur.close()
    con.close()
