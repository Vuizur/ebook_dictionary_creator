import json
import sqlite3
from sqlite3.dbapi2 import Cursor
import time
import os

import importlib.resources as pkg_resources
from ebook_dictionary_creator import data

# from create_databases.create_database import directly_link_transitive_base_form_relations
from ebook_dictionary_creator.database_creator.helper_functions import (
    remove_weird_characters_for_alternative_canonical,
)
from stressed_cyrillic_tools import (
    has_cyrillic_letters,
    remove_yo,
    unaccentify,
    remove_accent_if_only_one_syllable,
)

from ebook_dictionary_creator.database_creator.create_database import (
    directly_link_transitive_base_form_relations,
)
import re

DO_NOT_ADD_TRANSLATIONS = False  # Set true to reduce size of DB


def add_word_if_does_not_exist(cur: Cursor, canon_form: str):
    unaccentified = unaccentify(canon_form)
    lowercase = unaccentified.lower()
    without_yo = remove_yo(lowercase)
    res = cur.execute(
        "SELECT * FROM word WHERE canonical_form == ? OR alternative_canonical_form == ?",
        (canon_form, canon_form),
    ).fetchone()
    if res == None:
        cur.execute(
            "INSERT INTO word (canonical_form, word, word_lowercase, word_lower_and_without_yo) VALUES (?, ?, ?, ?)",
            (canon_form, unaccentified, lowercase, without_yo),
        )


def delete_inconsistent_canonical_forms(db_path):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    res = cur.execute(
        "SELECT word_id, canonical_form, alternative_canonical_form, word FROM word"
    ).fetchall()

    for word_id, can_form, alt_can_form, word in res:
        if (
            " " not in word
            and word != unaccentify(can_form)
            or (
                alt_can_form != None
                and "f " not in alt_can_form
                and "m " not in alt_can_form
                and word != unaccentify(alt_can_form)
            )
        ):

            print(word)
            print(can_form)
            if alt_can_form != None:
                print(alt_can_form)
            print("========")
            word_len = len(word)
            if unaccentify(can_form[0:word_len]) != word:
                cur.execute("DELETE FROM word WHERE word_id = ?", (word_id,))

    cur.close()
    con.close()


# TODO: Test


def has_at_least_one_not_form_of_sense(obj: dict):
    for sense in obj["senses"]:
        if "form_of" not in sense:
            return True
    return False


def forms_should_be_taken_from_word(obj: dict):
    try:
        if (
            obj["head_templates"][0]["args"]["cat2"] == "personal pronouns"
            and obj["word"] != "нечего"
            and obj["word"] != "некого"
            and obj["word"] != "аз"
        ):
            print(obj["word"])
            return False
    except:
        pass
    if has_at_least_one_not_form_of_sense(obj):
        return True
    else:
        for form in obj["forms"]:
            if form != "canonical" and form != "romanization":
                return True
        return False


def append_form_to_record(form: dict, form_dict: dict):
    form_tags = form["tags"]
    word_form = form["form"]

    if len(form_tags) == 2 and (
        ("nominative" in form_tags and "plural" in form_tags)
        or ("genitive" in form_tags and "plural")
    ):
        if "nominative" in form_tags and "plural" in form_tags:
            form_dict["nominative_plural_form"] = word_form
        elif "genitive" in form_tags and "plural" in form_tags:
            form_dict["genitive_plural_form"] = word_form
    else:
        for form_tag in form_tags:
            if form_tag == "canonical" and form_dict["canonical_form"] == None:
                form_dict["canonical_form"] = word_form
            elif form_tag == "canonical":
                form_dict[
                    "alternative_canonial_form"
                ] = remove_weird_characters_for_alternative_canonical(word_form)
            elif form_tag == "romanization":
                form_dict["romanized_form"] = word_form
            elif form_tag == "genitive":
                form_dict["genitive_form"] = word_form
            elif form_tag == "adjective":
                form_dict["adjective_form"] = word_form


def add_inflection_to_db(cur: Cursor, infl_str, base_word_pos, base_word_id, infl_tags):
    if infl_tags == ["perfective"] or infl_tags == ["imperfective"]:
        return  # These should have an entry on their own and might have different meanings
        # Inserting them fucks up some linkages I think

    infl_str = remove_accent_if_only_one_syllable(infl_str)
    unaccentified = unaccentify(infl_str)
    lowercase = unaccentified.lower()
    without_yo = remove_yo(lowercase)
    # TODO: Add check for already existing base form relation to base word id or so. If not, then create new entry
    # (This would be very important if I wanted to decline words myself with the application) because there are some different
    # words that have same pos and canonical form
    already_existing_word_id = cur.execute(
        "SELECT word_id FROM word WHERE canonical_form = ? AND pos = ?",
        (infl_str, base_word_pos),
    ).fetchone()

    if already_existing_word_id == None:
        cur.execute(
            "INSERT INTO word (word, canonical_form, pos, word_lowercase, word_lower_and_without_yo) \
            VALUES (?, ?, ?, ?, ?)",
            (unaccentified, infl_str, base_word_pos, lowercase, without_yo),
        )
        word_id = cur.lastrowid
    else:
        word_id = already_existing_word_id[0]
    cur.execute(
        "INSERT INTO form_of_word (word_id, base_word_id) VALUES (?, ?)",
        (word_id, base_word_id),
    )
    fow_id = cur.lastrowid
    for tag in infl_tags:
        cur.execute(
            "INSERT INTO case_tags (form_of_word_id, tag_text) VALUES (?, ?)",
            (fow_id, tag),
        )


def create_database_russian(database_path: str, wiktextract_json_path: str):
    try:
        os.remove(database_path)
    except:
        pass
    # with open('create_databases/create_db_tables_russian.sql', 'r') as sql_file:

    sql_script = pkg_resources.read_text(
        data, "create_db_tables_russian.sql"
    )  # sql_file.read()

    con = sqlite3.connect(database_path)
    cur = con.cursor()
    cur.executescript(sql_script)

    con.commit()

    alternative_yo_pattern = re.compile(".*Alternative spelling.*ё")
    print("Adding words from Wiktextract JSON")
    with open(wiktextract_json_path, "r", encoding="utf-8") as f:
        # tuple structure: word_id, base_word_string, grammar case
        form_of_words_to_add_later: "list[tuple(int, str, str)]" = []
        # inflection_table_forms: set[tuple(str, str)] = {}
        inflections = []
        for line in f:

            obj = json.loads(line)

            word_ipa_pronunciation = None
            form_dict: dict[str, str] = {
                "canonical_form": None,
                "alternative_canonial_form": None,
                "romanized_form": None,
                "genitive_form": None,
                "adjective_form": None,
                "nominative_plural_form": None,
                "genitive_plural_form": None,
            }

            word_pos = obj["pos"]
            try:
                for form in obj["forms"]:
                    append_form_to_record(form, form_dict)
            except:
                # print("Error for word")
                pass
            try:
                word_ipa_pronunciation = obj["sounds"][0]["ipa"]
            except:
                pass

            # skip all words where canonical_form does not have cyrillic letters because most likely it is something wrong like "n inan f"
            # and
            # check if Alternative spelling is in canonical form and then if a ё follows. If this is true, ignore word
            if form_dict["canonical_form"] != None and (
                alternative_yo_pattern.match(form_dict["canonical_form"]) != None
                or not has_cyrillic_letters(form_dict["canonical_form"])
            ):
                continue

            # remove everything after the first word because canonical forms are currently bugged in the wiktionary data
            # this creates inconsistent data, but for looking up the stress only words without space matter
            # TODO: fix and hope it gets solved upstream
            try:
                canonical_form_split = form_dict["canonical_form"].split(" ")
                # fix those wrong strings like балда f inan
                if len(canonical_form_split[1]) == 1:
                    form_dict["canonical_form"] = canonical_form_split[0]
            except:
                pass

            word_word = obj["word"]
            word_lowercase = word_word.lower()
            word_without_yo = remove_yo(word_lowercase)

            if form_dict["canonical_form"] != None:
                form_dict["canonical_form"] = remove_accent_if_only_one_syllable(
                    form_dict["canonical_form"]
                )
            else:
                form_dict["canonical_form"] = word_word

            try:
                # this could theoretically remove valid words from the library if there is a ё-version of them, but I am not
                # convinced that this is a problem -- Update: This is a problem if you look at the base category, but this version with
                # the senses might be safe. I should probably remove this entire block of code TODO: fix
                if (
                    "Russian spellings with е instead of ё"
                    in obj["senses"][0]["categories"]
                ):
                    continue
            except:
                pass

            cur.execute(
                "INSERT INTO word (pos, canonical_form, alternative_canonical_form, romanized_form, \
                ipa_pronunciation, word, word_lowercase, word_lower_and_without_yo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    word_pos,
                    form_dict["canonical_form"],
                    form_dict["alternative_canonial_form"],
                    form_dict["romanized_form"],
                    word_ipa_pronunciation,
                    word_word,
                    word_lowercase,
                    word_without_yo,
                ),
            )

            word_id = cur.lastrowid
            # word_id, base_word_string
            if "forms" in obj and forms_should_be_taken_from_word(obj):
                for infl_form in obj["forms"]:
                    if has_cyrillic_letters(infl_form["form"]) and "tags" in infl_form:
                        inflections.append(
                            (word_id, infl_form["form"], infl_form["tags"], word_pos)
                        )

            for sense in obj["senses"]:
                try:
                    if "Russian spellings with е instead of ё" in sense["categories"]:
                        # print(word_word)
                        continue
                except:
                    pass

                if "form_of" in sense:
                    for base_word in sense["form_of"]:
                        tag_string: str = ""
                        for tag in sense["tags"]:
                            tag_string += tag + " "
                        if sense["tags"] == [
                            "form-of",
                            "passive",
                        ] and has_at_least_one_not_form_of_sense(obj):
                            # print(word_word)
                            pass
                        else:
                            form_of_words_to_add_later.append(
                                (word_id, base_word["word"], tag_string)
                            )
                    # todo: fix for glosses that aren't the base word (pretty rare case)
                elif "alt_of" in sense:
                    for base_word in sense["alt_of"]:
                        form_of_words_to_add_later.append(
                            (word_id, base_word["word"], "")
                        )
                else:
                    cur.execute("INSERT INTO sense (word_id) VALUES (?)", (word_id,))
                    sense_id = cur.lastrowid
                    try:
                        for gloss in sense["glosses"]:
                            if DO_NOT_ADD_TRANSLATIONS:
                                continue
                            cur.execute(
                                "INSERT INTO gloss (sense_id, gloss_string, gloss_lang, gloss_source) VALUES(?, ?, ?, ?)",
                                (sense_id, gloss, "en", "wi"),
                            )
                    except:
                        pass

        con.commit()
        # add form of words after all data has been inserted
        print("Creating indices")
        cur.execute("CREATE INDEX word_word_index ON word(word);")
        cur.execute("CREATE INDEX word_canonical_form_index ON word(canonical_form);")
        # TODO: Don't know if this index maybe is not needed
        cur.execute(
            "CREATE INDEX alternative_word_canonical_form_index ON word(alternative_canonical_form);"
        )
        cur.execute(
            "CREATE INDEX canonical_alternative_canonical_index ON word(canonical_form, alternative_canonical_form);"
        )
        cur.execute("CREATE INDEX canfor_pos_index ON word(canonical_form, pos);")
        cur.execute("CREATE INDEX wordlo_pos_index ON word(word_lowercase, pos);")
        cur.execute(
            "CREATE INDEX wordlo_noyo_index ON word(word_lower_and_without_yo, pos);"
        )

        cur.execute("CREATE INDEX word_lowercase_index ON word(word_lowercase);")
        cur.execute(
            "CREATE INDEX word_lower_and_without_yo_index ON word(word_lower_and_without_yo);"
        )
        cur.execute("CREATE INDEX sense_word_id_index ON sense(word_id);")
        cur.execute("CREATE INDEX gloss_sense_id_index ON gloss(sense_id);")
        cur.execute("CREATE INDEX gloss_lang_index ON gloss(gloss_lang);")
        # No idea about this too
        cur.execute("CREATE INDEX gloss_source_index ON gloss(gloss_source);")
        cur.execute("CREATE INDEX word_id_index ON form_of_word(word_id);")
        cur.execute("CREATE INDEX base_word_id_index ON form_of_word(base_word_id);")
        cur.execute(
            "CREATE INDEX case_tags_fow_id_index ON case_tags(form_of_word_id);"
        )

        con.commit()
        print("Adding inflections to database")
        old_base_word_id = -99999
        already_added_tagged_infls: dict[str, set] = {}
        for base_word_id, infl_str, infl_tags, base_word_pos in inflections:
            if old_base_word_id != base_word_id:
                old_base_word_id = base_word_id
                already_added_tagged_infls = {}
            if "(" in infl_str and ")" in infl_str:
                split_word = infl_str.replace(")", "(").split("(")
                word1 = split_word[1] + split_word[2]
                word2 = split_word[2]
                add_inflection_to_db(cur, word1, base_word_pos, base_word_id, infl_tags)
                add_inflection_to_db(cur, word2, base_word_pos, base_word_id, infl_tags)
            elif already_added_tagged_infls.get(unaccentify(infl_str)) == set(
                infl_tags
            ):
                # print(infl_str)
                pass
            else:
                add_inflection_to_db(
                    cur, infl_str, base_word_pos, base_word_id, infl_tags
                )
                already_added_tagged_infls[unaccentify(infl_str)] = set(infl_tags)

    t0 = time.time()

    # with open("form_of_words_later.json", "w", encoding="utf-8") as outfile:
    #    json.dump(form_of_words_to_add_later, outfile, ensure_ascii=False, indent=4)

    # TODO: INSERT words if they are not already inserted this way - or do nothing
    for index in range(0, len(form_of_words_to_add_later), 1000):
        for word_id, base_word, case_text in form_of_words_to_add_later[
            index : index + 1000
        ]:
            unaccented_word = unaccentify(base_word)
            cur.execute(
                "INSERT OR IGNORE INTO form_of_word (word_id, base_word_id) \
    SELECT ?, COALESCE ( \
    (SELECT w.word_id FROM word w WHERE w.word = ?), \
    (SELECT w.word_id FROM word w WHERE w.canonical_form = ?), \
    (SELECT w.word_id FROM word w WHERE w.word = ?) \
    )",
                (word_id, base_word, base_word, unaccented_word),
            )
            # form_of_word_id = cur.lastrowid
            # cur.execute("INSERT OR IGNORE INTO gramm_case (form_of_word_id, case_text) VALUES (?,?)", (form_of_word_id, case_text))
    con.commit()
    print("Link transitive relations")
    directly_link_transitive_base_form_relations(cur)
    t1 = time.time()
    print(t1 - t0)

    con.commit()
    con.close()
