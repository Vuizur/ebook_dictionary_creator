from ebook_dictionary_creator.e_dictionary_creator.dictionary_creator import (
    DictionaryCreator,
    RussianDictionaryCreator,
)


def create_czech_english_dictionary():
    dict_creator = DictionaryCreator("Czech", "English")
    dict_creator.download_data_from_kaikki()
    dict_creator.create_database()
    dict_creator.export_to_tabfile()
    dict_creator.export_to_kindle(
        kindlegen_path="C:/Users/hanne/AppData/Local/Amazon/Kindle Previewer 3/lib/fc/bin/kindlegen.exe",
        try_to_fix_failed_inflections=False,  # This tries to fix kindle's problems with inflections.
        # For example, if oso is in the dictionary as a headword, it will only display this headword,
        # - if oso is the inflection of osar, osar will not be found. This tries to fix it.
        # Currently only works for latin scripts.
        author="Vuizur",
        title="Czech to English dictionary",
        mobi_path="Czech-English-dict",
    )
    dict_creator.export_to_stardict(
        "Vuizur", "Czech to English dictionary", "Czech-English-dict.ifo"
    )


def create_russian_dictionary():
    #dict_creator = RussianDictionaryCreator(kaikki_file_path="kaikki.org-dictionary-Russian.json")
    dict_creator = RussianDictionaryCreator()
    dict_creator.download_data_from_kaikki()
    #dict_creator.export_kaikki_utf8()
    dict_creator.create_database()
    dict_creator.add_data_from_openrussian()
    dict_creator.export_to_tabfile()
    

if __name__ == "__main__":
    dict_creator = DictionaryCreator("Latin", "English", database_path="Latin_English.db")
    #dict_creator.download_data_from_kaikki()
    #dict_creator.create_database()
    #dict_creator.export_to_tabfile()
    dict_creator.export_to_kindle(kindlegen_path="C:/Users/hanne/AppData/Local/Amazon/Kindle Previewer 3/lib/fc/bin/kindlegen.exe",
        try_to_fix_failed_inflections=False,
        author="Vuizur",
        title="Latin to English dictionary",
        mobi_path="Latin-English-dict",)

    quit()
    create_czech_english_dictionary()
    quit()
    #create_russian_dictionary()

    dict_creator = DictionaryCreator("Czech", "English")
    dict_creator.download_data_from_kaikki()
    dict_creator.create_database()
    dict_creator.export_to_kindle(
        kindlegen_path="C:/Users/hanne/AppData/Local/Amazon/Kindle Previewer 3/lib/fc/bin/kindlegen.exe",
        try_to_fix_failed_inflections=False,
        author="Vuizur",
        title="Polish to English dictionary",
        mobi_path="Polish-English-dict",
    )
    dict_creator.delete_database()
    dict_creator.delete_kaikki_file()
    quit()
    dict_creator = RussianDictionaryCreator(database_path="Russian_English.db")

    dict_creator.export_to_stardict("Vuizur", "Russian to English dictionary", "Russian-English-dict.ifo")


    quit()
    # create_czech_english_dictionary()

    #dict_creator = DictionaryCreator("Spanish")
    #dict_creator.download_data_from_kaikki()
    ##dict_creator.kaikki_file_path = "kaikki.org-dictionary-Czech.json"
    #dict_creator.create_database()
    #dict_creator.export_to_tabfile()
    #
#
    #quit()
#
    dict_creator = DictionaryCreator(
        "Czech", "English", None, database_path="Czech_English.db"
    )
    dict_creator.add_data_from_tatoeba()
    dict_creator.export_to_tabfile()
    #dict_creator.export_to_stardict(
    #    "Vuizur", "Czech to English dictionary", "Czech-English-dict.ifo"
    #)
    #dict_creator.export_to_kindle(
    #    kindlegen_path="C:/Users/hanne/AppData/Local/Amazon/Kindle Previewer 3/lib/fc/bin/kindlegen.exe",
    #    try_to_fix_failed_inflections=False,  # This tries to fix kindle's problems with inflections.
    #    # For example, if oso is in the dictionary as a headword, it will only display this headword,
    #    # - if oso is the inflection of osar, osar will not be found. This tries to fix it.
    #    # Currently only works for latin scripts.
    #    author="Vuizur",
    #    title="Czech to English dictionary new",
    #    mobi_path="Czech-English-dict-unfixed",
    #)
    ## dict_creator.export_to_tabfile()
#