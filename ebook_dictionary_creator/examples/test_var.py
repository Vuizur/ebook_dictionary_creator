from ebook_dictionary_creator.e_dictionary_creator.dictionary_creator import (
    RussianDictionaryCreator,
)


if __name__ == "__main__":
    rdc = RussianDictionaryCreator(
        kaikki_file_path="kaikki.org-dictionary-Russian.json"
    )
    rdc.create_database()
