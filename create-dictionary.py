from ebook_dictionary_creator import DictionaryCreator

dict_creator = DictionaryCreator("Malay", "English")#Source language, target language
dict_creator.download_data_from_kaikki()
dict_creator.create_database(use_raw_glosses=False)# No more raw glosses in the downloaded data from Kaikki.
dict_creator.export_to_tabfile()
dict_creator.export_to_kindle(
    kindlegen_path="/Applications/Kindle Previewer 3.app/Contents/lib/fc/bin/kindlegen",# Path to kindlegen executable
    try_to_fix_failed_inflections=False, # This tries to fix kindle's problems with inflections.
    # For example, if oso is in the dictionary as a headword, it will only display this headword, 
    # - if oso is the inflection of osar, osar will not be found. This tries to fix it. 
    # Currently only works for latin scripts.
    author="Vuizur",
    title="Malay to English dictionary",
    mobi_temp_folder_path="Malay-English-dict",
)