from ebook_dictionary_creator.e_dictionary_creator.dictionary_creator import (
    DictionaryCreator,
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


if __name__ == "__main__":
    #create_czech_english_dictionary()

    dict_creator = DictionaryCreator("Polish", "English")
    dict_creator.download_data_from_kaikki()
    dict_creator.create_database()
    dict_creator.export_to_tabfile()

    quit()

    dict_creator = DictionaryCreator(
        "Czech", "English", None, database_path="Czech_English.db"
    )
    dict_creator.export_to_tabfile()
    dict_creator.export_to_stardict(
        "Vuizur", "Czech to English dictionary", "Czech-English-dict.ifo"
    )
    dict_creator.export_to_kindle(
        kindlegen_path="C:/Users/hanne/AppData/Local/Amazon/Kindle Previewer 3/lib/fc/bin/kindlegen.exe",
        try_to_fix_failed_inflections=False,  # This tries to fix kindle's problems with inflections.
        # For example, if oso is in the dictionary as a headword, it will only display this headword,
        # - if oso is the inflection of osar, osar will not be found. This tries to fix it.
        # Currently only works for latin scripts.
        author="Vuizur",
        title="Czech to English dictionary new",
        mobi_path="Czech-English-dict-unfixed",
    )
    # dict_creator.export_to_tabfile()
