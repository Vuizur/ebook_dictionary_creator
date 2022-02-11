from time import time
from create_databases.create_database_russian import create_database_russian, delete_inconsistent_canonical_forms
from create_databases.create_database import create_database, remove_spanish_pronouns_from_inflection
from create_databases.convert_file_to_utf8 import convert_file_to_utf8
from create_databases.create_openrussian_database_from_csv import create_openrussian_database
from create_databases.add_openrussian_to_database import add_openrussian_to_db
from create_kindle_dict.create_kindle_dict import create_kindle_dict
from create_kindle_dict.create_kindle_dict_from_db_russian import create_kindle_dict_from_db, create_py_glossary_and_export
import os

from create_kindle_dict.create_tab_file import create_nonkindle_dict

def create_ru_db_full(wiktextract_json_input_path, create_openrussian_db: bool, convert_utf8 = True,
     openrussian_db_path = "openrussian.db", output_database_path = "russian_dict.db", intermediate_utf8_json_path="russian-dict.json"):
    """Creates an SQLite database containing the data from Wiktextract combined with data by OpenRussian\n
    The Wiktextract data can be downloaded from kaikki.org"""
    if convert_utf8:
        convert_file_to_utf8(wiktextract_json_input_path, intermediate_utf8_json_path)
        print("Wiktextract file has been converted to UTF-8")
    #This creates the Wiktextract portion of the database
    create_database_russian(output_database_path, intermediate_utf8_json_path)
    print("Wiktextract data has been added to database")
    if create_openrussian_db:
        create_openrussian_database(openrussian_db_path)
    add_openrussian_to_db(output_database_path, openrussian_db_path)
    print("OpenRussian data has been added to database")

def create_db_full(wiktextract_json_input_path: str, language: str, output_database_path: str, intermediate_utf8_json_path: str):
    convert_file_to_utf8(wiktextract_json_input_path, intermediate_utf8_json_path)
    print("File has been converted to UTF-8")
    create_database(output_database_path, intermediate_utf8_json_path, language)

def create_dictionary_from_zero(input_lang, output_lang, author, dict_name, 
    fix_kindle_stupidity = True, wiktextract_json_input_path = None):

    time1 = time()

    dict_database_path = "compiled_databases/" + input_lang + "_dict.db"
    intermediate_utf8_path = "utf8_json/" + input_lang + "-dict.json"
    kindle_dict_out_path = input_lang + "_dict"
    if wiktextract_json_input_path != None:
        convert_file_to_utf8(wiktextract_json_input_path, intermediate_utf8_path)
        print("File has been converted to UTF-8")
    create_database(dict_database_path, intermediate_utf8_path, input_lang)
    create_kindle_dict(dict_database_path, input_lang, output_lang, kindle_dict_out_path, author, dict_name, fix_kindle_stupidity)
    
    output_path = "compiled_kindle_dictionaries/" + dict_name + ".mobi"
    while os.path.exists(output_path):
        output_path = output_path + "_new"

    os.replace(kindle_dict_out_path + "/OEBPS/content.mobi", output_path)

    time2 = time()
    print("Dictionary created in " + str((time2 - time1) % 60) + " minutes.")

if __name__ == "__main__":
    #create_ru_db_full("kaikki/kaikki.org-dictionary-Russian.json", create_openrussian_db=False, convert_utf8=False)
    #create_db_full("kaikki.org-dictionary-Spanish_new.json")
    #convert_file_to_utf8("kaikki.org-dictionary-English.json", "english_dict.json")
    #create_db_full("kaikki.org-dictionary-English.json", language=Language.ENGLISH, 
    #    output_database_path="english_dict.db", intermediate_utf8_json_path="english_dict.json")
    #convert_file_to_utf8("kaikki.org-dictionary-Italian.json", "italian-dict.json")
    #create_database("italian_dict.db", "italian-dict.json", Language.ITALIAN)
    #create_kindle_dict("italian_dict.db", "Italian", "English", "italian_dict", "Vuizur", "Italian-English Dictionary")
    
    #create_kindle_dict("english_dict.db", "English", "English", "english_dict", "Vuizur", "English Monolingual Dictionary")
    #create_database("compiled_databases/spanish_dict.db", "utf8_json/Spanish-dict.json", language="Spanish")
   
    #create_kindle_dict("spanish_dict.db", "Spanish", "English", "spanish_dict", "Vuizur", "Spanish-English Dictionary", try_to_fix_kindle_lookup_stupidity=True)

    #delete_inconsistent_canonical_forms("russian_dict.db")

    #### From Zero
    create_dictionary_from_zero("Spanish", "English", "Vuizur", "Spanish-English dictionary", wiktextract_json_input_path="kaikki/kaikki.org-dictionary-Spanish.json")
    #create_dictionary_from_zero("Catalan", "English", "Vuizur", "Catalan-English Dictionary", wiktextract_json_input_path="kaikki/kaikki.org-dictionary-Catalan.json")
    #create_dictionary_from_zero("Arabic", "English", "Vuizur", "Arabic-English dictionary", wiktextract_json_input_path="kaikki/kaikki.org-dictionary-Arabic.json")
    #create_dictionary_from_zero("Polish", "English", "Vuizur", "Polish-English dictionary", wiktextract_json_input_path="kaikki/kaikki.org-dictionary-Polish.json")
    #create_dictionary_from_zero("Portuguese", "English", "Vuizur", "Portuguese-English dictionary", wiktextract_json_input_path="kaikki/kaikki.org-dictionary-Portuguese.json")
    #create_dictionary_from_zero("Finnish", "English", "Vuizur", "Finnish-English dictionary", wiktextract_json_input_path="kaikki/kaikki.org-dictionary-Finnish.json")
    #create_dictionary_from_zero("Latin", "English", "Vuizur", "Latin-English dictionary", wiktextract_json_input_path="kaikki/kaikki.org-dictionary-Latin.json")
    #create_dictionary_from_zero("Swedish", "English", "Vuizur", "Swedish-English dictionary", wiktextract_json_input_path="kaikki/kaikki.org-dictionary-Swedish.json")
    #create_tabfile("compiled_databases/Spanish_dict.db", "spanish.txt")
    #convert_file_to_utf8("kaikki/kaikki.org-dictionary-Russian.json", )
    #create_database_russian("russian.db", "russian-dict.json")
    #create_py_glossary_and_export("russian_dict.db", "STARDICT")
    
    #print(remove_spanish_pronouns_from_inflection("no te vayas"))