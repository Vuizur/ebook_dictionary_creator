from ebook_dictionary_creator import DictionaryCreator
from ebook_dictionary_creator.e_dictionary_creator.create_all_dictionaries import AllLanguageDictCreator, create_lua_code_for_koreader
from ebook_dictionary_creator.e_dictionary_creator.dictionary_creator import RussianDictionaryCreator
from ebook_dictionary_creator.e_dictionary_creator.helper_scripts import convert_stardict_to_tabfile_and_back

def create_all_languages():
    #AllLanguageDictCreator.package_all_dictionaries("D:\Wiktionary-Dictionaries")
    ldc = AllLanguageDictCreator(
        kindlegen_path="C:/Users/hanne/AppData/Local/Amazon/Kindle Previewer 3/lib/fc/bin/kindlegen.exe",
        author="Vuizur",
        dictionary_folder="D:/Wiktionary-Dictionaries",
    )
   
    ldc.create_all_dictionaries("progress.txt")

# For KOReader
def create_lua_file():
    create_lua_code_for_koreader("D:/Wiktionary-Dictionaries")

def create_italian_dict():
    dc = DictionaryCreator("Italian")
    dc.download_data_from_kaikki()
    dc.create_database()
    dc.export_to_tabfile()


def create_russian_dictionary():
    # dict_creator = RussianDictionaryCreator(kaikki_file_path="kaikki.org-dictionary-Russian.json")
    dict_creator = RussianDictionaryCreator()
    dict_creator.download_data_from_kaikki()
    # dict_creator.export_kaikki_utf8()
    dict_creator.create_database()
    dict_creator.add_data_from_openrussian()
    dict_creator.export_to_tabfile("Russian-English-dict.tsv")
    dict_creator.export_to_stardict("Vuizur", "Russian - English Wiktionary + OpenRussian dictionary")

if __name__ == "__main__":
    #convert_stardict_to_tabfile_and_back("Russian_English.ifo", "Russian_English2.ifo")
    #quit()
    create_russian_dictionary()
    quit()
    #create_all_languages()
    #create_lua_file()
    #create_italian_dict()
    dc = DictionaryCreator("Italian")
    dc.download_data_from_kaikki()
    dc.create_database()
    dc.export_to_tabfile()