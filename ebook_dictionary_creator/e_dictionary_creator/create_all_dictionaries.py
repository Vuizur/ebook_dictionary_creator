import importlib.resources as pkg_resources
from ebook_dictionary_creator import data
from ebook_dictionary_creator.e_dictionary_creator.dictionary_creator import DictionaryCreator

class AllLanguageDictCreator():
    def __init__(self, dictionary_folder: str = "dictionaries"):
        self.languages = pkg_resources.read_text(data, "languages.txt").splitlines()
        self.dictionary_folder = dictionary_folder

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
            if language not in downloaded_languages:
                print("Creating dictionary for " + language)

                dict_creator = DictionaryCreator(language)
                dict_creator.download_data_from_kaikki()
                dict_creator.create_database()
                dictionary_name = f"{language}-English Wiktionary dictionary"
                dict_creator.export_to_tabfile(f"{self.dictionary_folder}/{dictionary_name}.tsv")
                # TODO: Kindle, kindle with fixed inflections, stardict
                

                # Add language to progress file
                with open(progress_file_path, "a", encoding="utf-8") as progress_file:
                    progress_file.write(language + "\n")
                print("Dictionary for " + language + " created")


if __name__ == "__main__":
    ldc = AllLanguageDictCreator()
    for language in ldc.languages:
        print(language)

