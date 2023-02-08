import json
import os
import shutil
import sqlite3
import requests

from ebook_dictionary_creator.database_creator import (
    create_database,
    create_openrussian_database_from_csv,
)
from ebook_dictionary_creator.database_creator.create_database_russian import (
    create_database_russian,
)
from ebook_dictionary_creator.database_creator.add_openrussian_to_database import (
    add_openrussian_to_db_with_linkages,
)
from ebook_dictionary_creator.e_dictionary_creator.create_kindle_dict import (
    create_kindle_dict,
)
from ebook_dictionary_creator.e_dictionary_creator.create_kindle_dict_from_db_russian import (
    create_py_glossary_and_export,
)
from ebook_dictionary_creator.e_dictionary_creator.create_tab_file import (
    create_nonkindle_dict,
)
from ebook_dictionary_creator.e_dictionary_creator.tatoeba_creator import (
    TatoebaAugmenter,
)

LANGUAGES_WITH_STRESS_MARKED_IN_DICT = [
    "Russian",
    "Ukraininian",
    "Belarusian",
    "Bulgarian",
    "Rusyn",
]
"""Languages that have the stress marked in a dictionary, but not in general texts."""


def convert_line_endings(file_path: str):
    """Converts line endings in the given file to Unix style"""
    with open(file_path, "rb") as file:
        data = file.read()

    with open(file_path, "wb") as file:
        file.write(data.replace(b"\r\n", b"\n"))


class DictionaryCreator:

    # Initialize the class with the source language and target language
    def __init__(
        self,
        source_language: str,
        target_language: str = "English",
        kaikki_file_path=None,
        database_path=None,
    ):
        self.source_language = source_language
        self.target_language = target_language
        self.kaikki_file_path = kaikki_file_path
        self.database_path = database_path

    def download_data_from_kaikki(self, kaikki_file_path: str = None, overwrite_if_already_exists=False):
        # This downloads the data from kaikki.org, with the following format https://kaikki.org/dictionary/Czech/kaikki.org-dictionary-Czech.json
        # Only replace Czech with whatever language you want to download
        if kaikki_file_path == None:
            kaikki_file_path = "kaikki.org-dictionary-" + self.source_language + ".json"

        self.kaikki_file_path = kaikki_file_path

        if os.path.exists(kaikki_file_path) and not overwrite_if_already_exists:
            print("Kaikki file already exists...")
        else:
            with open(kaikki_file_path, "w", encoding="utf-8") as f:
                lang_nospaces = self.source_language.replace(" ", "").replace("-", "").replace("'", "")
                f.write(
                    requests.get(
                        f"https://kaikki.org/dictionary/{self.source_language}/kaikki.org-dictionary-{lang_nospaces}.json"
                    ).text
                )

    def create_database(self, database_path: str = None, use_raw_glosses=True):
        # This creates the database from the kaikki.org file
        if database_path == None:
            database_path = self.source_language + "_" + self.target_language + ".db"
        create_database.create_database(
            database_path, self.kaikki_file_path, self.source_language, use_raw_glosses
        )
        self.database_path = database_path

    def add_data_from_tatoeba(self):

        # Get all the words from the database
        conn = sqlite3.connect(self.database_path)
        c = conn.cursor()
        c.execute("SELECT word FROM word")
        words = c.fetchall()
        # Convert to a proper list
        exception_word_list = {word[0] for word in words}
        self.tatoeba_creator = TatoebaAugmenter(
            self.source_language, self.target_language, exception_word_list
        )
        test_output = (
            self.tatoeba_creator.get_word_and_html_for_all_words_not_in_word_list()
        )
        # Print dictionary to file
        with open("tatoeba_output.txt", "w", encoding="utf-8") as f:
            f.write(str(test_output))

    def export_to_tabfile(self, tabfile_path: str = None):
        # This exports the database to a tabfile
        if tabfile_path == None:
            tabfile_path = self.source_language + "_" + self.target_language + ".tsv"
        create_nonkindle_dict(self.database_path, tabfile_path, "Tabfile", self.source_language, self.target_language)
        self.tabfile_path = tabfile_path

    def export_to_stardict(self, author: str, title: str, stardict_path: str = None):
        """Exports the dictionary to a folder specified by stardict_path."""
        # This exports the database to a stardict file
        if stardict_path.lower().endswith(".ifo"):
            stardict_path = stardict_path[:-4]
        if stardict_path == None:
            stardict_path = (
                self.source_language + "_" + self.target_language
            )  # + ".ifo"

        # Create folder if it doesn't exist
        if not os.path.exists(stardict_path):
            os.makedirs(stardict_path)
        ifo_path = stardict_path + "/" + title + ".ifo"

        create_nonkindle_dict(
            self.database_path,
            ifo_path,
            "Stardict",
            self.source_language,
            self.target_language,
            author,
            title,
        )

        # Windows line endings are not supported by sdcv/KOReader, so convert to Unix style
        if os.name == "nt":
            convert_line_endings(ifo_path)

        self.stardict_path = ifo_path

    def export_to_kindle(
        self,
        kindlegen_path: str,
        try_to_fix_failed_inflections: str,
        author: str,
        title: str,
        mobi_temp_folder_path: str = None,
        mobi_output_file_path: str = None,
    ):
        # if mobi path ends on .mobi, remove the ending
        if mobi_temp_folder_path.lower().endswith(".mobi"):
            mobi_temp_folder_path = mobi_temp_folder_path[:-4]
        if mobi_temp_folder_path == None:
            mobi_temp_folder_path = (
                self.source_language + "_" + self.target_language
            )  # + ".mobi"

        if mobi_output_file_path == None:
            mobi_output_file_path = mobi_temp_folder_path + ".mobi"
        create_kindle_dict(
            self.database_path,
            self.source_language,
            self.target_language,
            mobi_temp_folder_path,
            author,
            title,
            kindlegen_path,
            try_to_fix_kindle_lookup_stupidity=try_to_fix_failed_inflections,
        )
        shutil.move(
            mobi_temp_folder_path + "/OEBPS/content.mobi", mobi_output_file_path
        )

        shutil.rmtree(mobi_temp_folder_path)

        self.mobi_path = mobi_output_file_path

    def export_kaikki_utf8(self, kaikki_utf8_path: str = None):
        if kaikki_utf8_path == None:
            kaikki_utf8_path = (
                self.source_language + "_" + self.target_language + "_utf8.json"
            )
        # This exports the database to a kaikki.org file
        with open(self.kaikki_file_path, "r", encoding="utf-8") as input, open(
            kaikki_utf8_path, "w", encoding="utf-8"
        ) as out:
            for line in input:
                data = json.loads(line)
                json.dump(data, out, ensure_ascii=False)
                out.write("\n")

    def delete_database(self):
        # This deletes the database
        os.remove(self.database_path)

    def delete_kaikki_file(self):
        # This deletes the kaikki.org file
        os.remove(self.kaikki_file_path)


class RussianDictionaryCreator(DictionaryCreator):
    def __init__(self, database_path: str = None, kaikki_file_path: str = None):
        super().__init__("Russian", "English", kaikki_file_path, database_path)

    def add_data_from_openrussian(self, openrussian_db_path: str = None):
        if openrussian_db_path == None:
            openrussian_db_path = "openrussian.db"
        if not os.path.exists(openrussian_db_path):
            create_openrussian_database_from_csv.create_openrussian_database(
                openrussian_db_path
            )
        add_openrussian_to_db_with_linkages(self.database_path, openrussian_db_path)

    def create_database(self, database_path: str = None, use_raw_glosses=True):
        if database_path == None:
            database_path = self.source_language + "_" + self.target_language + ".db"
        create_database_russian(database_path, self.kaikki_file_path)
        self.database_path = database_path

    def export_to_tabfile(self, tabfile_path: str = None):
        if tabfile_path == None:
            tabfile_path = self.source_language + "_" + self.target_language + ".tsv"
        create_py_glossary_and_export(self.database_path, tabfile_path, "Tabfile")

    def export_to_stardict(self, author: str, title: str, stardict_path: str = None):
        if stardict_path == None:
            stardict_path = self.source_language + "_" + self.target_language + ".ifo"
        create_py_glossary_and_export(self.database_path, stardict_path, "Stardict", author, title)

    def export_to_kindle(
        self,
        kindlegen_path: str,
        try_to_fix_failed_inflections: str,
        author: str,
        title: str,
        mobi_temp_folder_path: str = None,
        mobi_output_file_path: str = None,
    ):
        if mobi_temp_folder_path.lower().endswith(".mobi"):
            mobi_temp_folder_path = mobi_temp_folder_path[:-4]
        if mobi_temp_folder_path == None:
            mobi_temp_folder_path = (
                self.source_language + "_" + self.target_language
            )  # + ".mobi"

        if mobi_output_file_path == None:
            mobi_output_file_path = mobi_temp_folder_path + ".mobi"

        create_py_glossary_and_export(
            self.database_path, mobi_temp_folder_path, "Mobi", author, title, kindlegen_path
        )
        shutil.move(
            mobi_temp_folder_path + "/OEBPS/content.mobi", mobi_output_file_path
        )

        shutil.rmtree(mobi_temp_folder_path)

        self.mobi_path = mobi_output_file_path