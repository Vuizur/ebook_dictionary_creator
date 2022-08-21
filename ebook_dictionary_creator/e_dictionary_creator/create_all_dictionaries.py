import importlib.resources as pkg_resources
import os
from ebook_dictionary_creator import data
from ebook_dictionary_creator.e_dictionary_creator.dictionary_creator import DictionaryCreator

class AllLanguageDictCreator():
    def __init__(self, kindlegen_path: str, author: str, dictionary_folder: str = "dictionaries"):
        self.languages = pkg_resources.read_text(data, "languages.txt").splitlines()
        self.dictionary_folder = dictionary_folder
        self.kindlegen_path = kindlegen_path
        self.author = author
        # Create dictionary folder if it does not exist
        if not os.path.exists(self.dictionary_folder):
            os.makedirs(self.dictionary_folder)
        # As of now Finnish doesn't work, probably because there are too many inflections
        # Kindlegen doesn't know Esperanto
        self.DONT_EXPORT_TO_KINDLE_LANGUAGES = ["Finnish", "Esperanto", "Serbo-Croatian", "Translingual", "Middle English"]
        # This has probably too many relations that lead to a memory overflow when creating a database
        self.SKIP_LANGUAGES = ["Catalan", "Dutch", "Swedish"]

    def create_dictionary_for_language(self, language: str):
        print("Creating dictionary for " + language)
        dict_creator = DictionaryCreator(language)
        dict_creator.download_data_from_kaikki()
        dict_creator.create_database()
        dictionary_name = f"{language}-English Wiktionary dictionary"
        # Create {self.dictionary_folder}/{dictionary_name} folder if it does not exist
        #if not os.path.exists(f"{self.dictionary_folder}/{dictionary_name}"):
        #    os.makedirs(f"{self.dictionary_folder}/{dictionary_name}")
        dict_creator.export_to_tabfile(f"{self.dictionary_folder}/{dictionary_name}.tsv")
        dict_creator.export_to_stardict(
            self.author, dictionary_name, f"{self.dictionary_folder}/{dictionary_name} stardict"
        )
        if language not in self.DONT_EXPORT_TO_KINDLE_LANGUAGES:
            dict_creator.export_to_kindle(
                kindlegen_path=self.kindlegen_path,
                try_to_fix_failed_inflections=False, 
                author=self.author,
                title=dictionary_name,
                mobi_temp_folder_path=dictionary_name,
                mobi_output_file_path=f"{self.dictionary_folder}/{dictionary_name}.mobi"
            )             
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
            if language not in downloaded_languages and language not in self.SKIP_LANGUAGES:
                
                self.create_dictionary_for_language(language)
                # Add language to progress file
                with open(progress_file_path, "a", encoding="utf-8") as progress_file:
                    progress_file.write(language + "\n")
                print("Dictionary for " + language + " created")


if __name__ == "__main__":

    # Set current directory to D:\Wiktionary-Dictionaries

    ldc = AllLanguageDictCreator(kindlegen_path="C:/Users/hanne/AppData/Local/Amazon/Kindle Previewer 3/lib/fc/bin/kindlegen.exe", author="Vuizur", dictionary_folder="D:/Wiktionary-Dictionaries")
    ldc.create_all_dictionaries("progress.txt")
