from ebook_dictionary_creator import DictionaryCreator
from ebook_dictionary_creator.e_dictionary_creator.create_all_dictionaries import AllLanguageDictCreator, create_lua_code_for_koreader

def create_all_languages():
    #AllLanguageDictCreator.package_all_dictionaries("D:\Wiktionary-Dictionaries")
    ldc = AllLanguageDictCreator(
        kindlegen_path="C:/Users/hanne/AppData/Local/Amazon/Kindle Previewer 3/lib/fc/bin/kindlegen.exe",
        author="Vuizur",
        dictionary_folder="D:/Wiktionary-Dictionaries",
    )
   
    ldc.create_all_dictionaries("progress.txt")

def create_lua_file():
    create_lua_code_for_koreader("D:/Wiktionary-Dictionaries")

def create_italian_dict():
    dc = DictionaryCreator("Italian")
    dc.download_data_from_kaikki()
    dc.create_database()
    dc.export_to_tabfile()

if __name__ == "__main__":
    #create_all_languages()
    create_lua_file()