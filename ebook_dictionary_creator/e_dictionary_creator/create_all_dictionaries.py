import importlib.resources as pkg_resources
import re
import shutil
import tarfile
import os
from ebook_dictionary_creator import data
from ebook_dictionary_creator.e_dictionary_creator.dictionary_creator import (
    DictionaryCreator,
)
import zipfile


class AllLanguageDictCreator:
    def __init__(
        self, kindlegen_path: str, author: str, dictionary_folder: str = "dictionaries"
    ):
        self.languages = pkg_resources.read_text(data, "languages.txt").splitlines()
        self.dictionary_folder = dictionary_folder
        self.kindlegen_path = kindlegen_path
        self.author = author
        # Create dictionary folder if it does not exist
        if not os.path.exists(self.dictionary_folder):
            os.makedirs(self.dictionary_folder)
        # As of now Finnish doesn't work, probably because there are too many inflections
        # Kindlegen doesn't know Esperanto, serbo-croatian, translingual, middle english

        self.DONT_EXPORT_TO_KINDLE_LANGUAGES = [
            "Finnish",  # Too many inflections
            "Esperanto",  # Kindlegen doesn't know Esperanto
            "Serbo-Croatian",
            "Translingual",
            "Middle English",  # Not in pyglossary
            "Korean",
            "Ancient Greek",  # Not in pyglossary
            "Asturian",  # Not in pyglossary
            "Tagalog",
            "Cebuano",  # Not in pyglossary
            "Gothic",  # Not in pyglossary
            "Ido",
            "Old English",  # Not in pyglossary
            "Old Norse",  # Not in pyglossary
            "Swahili",  # Simply too many inflections
            "Old Armenian",  # Not in pyglossary
            "Norman",  # Not in pyglossary
            "Cantonese",  # Not in pyglossary
            "Khmer",
            "Old French",  # Not in pyglossary
            "Yiddish",
            "Pali",
            "Ladin",  # Not in pyglossary
            "Navajo",
            "Burmese",
            "Northern Kurdish",  # Not in
            "Adyghe",  # Not in pyglossary
            "Occitan",  # Not in pyglossary
            "Northern Sami",  # Doesn't know Kindlegen
            "Old Irish",  # dk
            "Yoruba",  # dk
            "Old Church Slavonic",  # Not in Pyglossary
            "Cimbrian",  # Not in Pyglossary
            "Venetian",  # Not in Pyglossary
            "Middle French",  # Not in Pyglossary
            "Scots",  # Not in Pyglossary
            "Old Norse",  # Not in Pyglossary
            "Classical Nahuatl",  # Not in Pyglossary
        ]
        # This has probably too many relations that lead to a memory overflow when creating a database (or swahili, which is simply too slow)
        self.SKIP_LANGUAGES = [
            "Catalan",
            "Dutch",
            "Swedish",
            "Egyptian",
            "Nepali",
        ]  # , "Swahili"]
        # These languages above I should probably fix at some point
        self.log_file_path = "log.txt"

    @staticmethod
    def package_stardict_dictionary(dictionary_folder: str):
        if os.path.isdir(dictionary_folder):
            with tarfile.open(f"{dictionary_folder}.tar.gz", "w:gz") as tar:
                # Get the name of the folder (and remove the base path)
                folder_name = os.path.basename(dictionary_folder)
                tar.add(dictionary_folder, arcname=folder_name)
        # Delete dictionary folder
        if os.path.isdir(dictionary_folder):
            shutil.rmtree(dictionary_folder)

    def create_dictionary_for_language(self, language: str):
        print("Creating dictionary for " + language)
        dict_creator = DictionaryCreator(language)
        dict_creator.download_data_from_kaikki()
        dict_creator.create_database()
        dictionary_name = f"{language}-English Wiktionary dictionary"
        # Create {self.dictionary_folder}/{dictionary_name} folder if it does not exist
        # if not os.path.exists(f"{self.dictionary_folder}/{dictionary_name}"):
        #    os.makedirs(f"{self.dictionary_folder}/{dictionary_name}")
        dict_creator.export_to_tabfile(
            f"{self.dictionary_folder}/{dictionary_name}.tsv"
        )

        # If the created file is larger than 100 mb, package it as a zip file and delete the tsv file
        if (
            os.path.getsize(f"{self.dictionary_folder}/{dictionary_name}.tsv")
            > 100000000
        ):
            with zipfile.ZipFile(
                f"{self.dictionary_folder}/{dictionary_name}.zip",
                "w",
                zipfile.ZIP_DEFLATED,
            ) as zip_file:
                zip_file.write(
                    f"{self.dictionary_folder}/{dictionary_name}.tsv",
                    f"{dictionary_name}.tsv",
                )
            os.remove(f"{self.dictionary_folder}/{dictionary_name}.tsv")
        stardict_folder = f"{self.dictionary_folder}/{dictionary_name} stardict"
        dict_creator.export_to_stardict(
            self.author,
            dictionary_name,
            stardict_folder,
        )
        self.package_stardict_dictionary(stardict_folder)
        if language not in self.DONT_EXPORT_TO_KINDLE_LANGUAGES:
            try:
                dict_creator.export_to_kindle(
                    kindlegen_path=self.kindlegen_path,
                    try_to_fix_failed_inflections=False,
                    author=self.author,
                    title=dictionary_name,
                    mobi_temp_folder_path=dictionary_name,
                    mobi_output_file_path=f"{self.dictionary_folder}/{dictionary_name}.mobi",
                )
            except Exception as e:
                print(e)
                with open(self.log_file_path, "a", encoding="utf-8") as log_file:
                    log_file.write(f"{language}: {e}\n")
        dict_creator.delete_database()
        dict_creator.delete_kaikki_file()

    def create_all_dictionaries(self, progress_file_path: str):
        # Load progress file, otherwise create it
        try:
            with open(progress_file_path, "r", encoding="utf-8") as progress_file:
                downloaded_languages = progress_file.read().splitlines()
        except FileNotFoundError:
            downloaded_languages = []
        # Create all dictionaries
        # Iterate over all languages that have not been downloaded yet
        for language in self.languages:
            if (
                language not in downloaded_languages
                and language not in self.SKIP_LANGUAGES
            ):

                self.create_dictionary_for_language(language)
                # Add language to progress file
                with open(progress_file_path, "a", encoding="utf-8") as progress_file:
                    progress_file.write(language + "\n")
                print("Dictionary for " + language + " created")

    @staticmethod
    def package_all_dictionaries(dictionary_folder: str) -> None:
        # Iterates over all folders in dictionary_folder and creates a tar.gz file for each
        for folder in os.listdir(dictionary_folder):
            if os.path.isdir(f"{dictionary_folder}/{folder}"):
                with tarfile.open(
                    f"{dictionary_folder}/{folder}.tar.gz", "w:gz"
                ) as tar:
                    tar.add(f"{dictionary_folder}/{folder}", arcname=folder)


def create_lua_code_for_koreader(stardict_tar_gz_folder: str):

    dictionary_template = """
    {{
        name = "{name}",
        lang_in = "{lang_in}",
        lang_out = "{lang_out}",
        entries = {entry_count},
        license = "Dual-licensed under CC-BY-SA 3.0 and GFDL",
        url = "{url}",
    }}"""
    lua_strings = []

    # Iterate through all tar.gz files in stardict_tar_gz_folder
    for file in os.listdir(stardict_tar_gz_folder):
        if file.endswith(".tar.gz"):
            # Get the name of the dictionary
            dictionary_name = file.replace(".tar.gz", "").rsplit(" ", 1)[0]
            # Get the language of the dictionary
            in_language = dictionary_name.split("-English Wiktionary dictionary")[0]
            # Create a dictionary folder
            # dictionary_folder = f"{stardict_tar_gz_folder}/{dictionary_name}"
            # if not os.path.exists(dictionary_folder):
            #    os.makedirs(dictionary_folder)
            # Extract the tar.gz file
            with tarfile.open(f"{stardict_tar_gz_folder}/{file}", "r:gz") as tar:
                tar.extractall(stardict_tar_gz_folder)
            dictionary_folder = f"{stardict_tar_gz_folder}/{dictionary_name} stardict"
            # Load the ifo file
            with open(
                f"{dictionary_folder}/{dictionary_name}.ifo", "r", encoding="utf-8"
            ) as ifo_file:
                ifo_file_content = ifo_file.read()

            # Delete the unpacked tar.gz file
            shutil.rmtree(dictionary_folder)

            # Get the number of entries
            entry_count = re.search(r"wordcount=(\d+)", ifo_file_content).group(1)

            # Url like https://github.com/Vuizur/Wiktionary-Dictionaries/raw/master/Welsh-English%20Wiktionary%20dictionary.tsv
            url = f"https://github.com/Vuizur/Wiktionary-Dictionaries/raw/master/{dictionary_name} stardict.tar.gz".replace(
                " ", "%20"
            )
            # Create a lua file for Koreader
            lua_strings.append(
                dictionary_template.format(
                    name=dictionary_name,
                    lang_in=in_language,
                    lang_out="English",
                    entry_count=entry_count,
                    url=url,
                )
            )
    # Write the lua file
    with open(
        f"{stardict_tar_gz_folder}/koreader.lua", "w", encoding="utf-8"
    ) as lua_file:
        lua_file.write(",".join(lua_strings))
