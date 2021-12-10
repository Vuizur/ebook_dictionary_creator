from create_databases.create_database_russian import create_database_russian
from create_databases.create_database_spanish import create_database_spanish
from create_databases.convert_file_to_utf8 import convert_file_to_utf8
from create_databases.create_openrussian_database_from_csv import create_openrussian_database
from create_databases.add_openrussian_to_database import add_openrussian_to_db

def create_ru_db_full(wiktextract_json_input_path, openrussian_db_path = "openrussian.db", output_database_path = "russian_dict.db", intermediate_utf8_json_path="russian-dict.json"):
    """Creates an SQLite database containing the data from Wiktextract combined with data by OpenRussian\n
    The Wiktextract data can be downloaded from kaikki.org"""
    convert_file_to_utf8(wiktextract_json_input_path, intermediate_utf8_json_path)
    print("Wiktextract file has been converted to UTF-8")
    #This creates the Wiktextract portion of the database
    create_database_russian(output_database_path, intermediate_utf8_json_path)
    print("Wiktextract data has been added to database")
    create_openrussian_database(openrussian_db_path)
    add_openrussian_to_db(output_database_path, openrussian_db_path)
    print("OpenRussian data has been added to database")

def create_es_db_full(wiktextract_json_input_path,output_database_path="spanish_dict.db", intermediate_utf8_json_path="spanish-dict.json"):
    convert_file_to_utf8(wiktextract_json_input_path, intermediate_utf8_json_path)
    print("File has been converted to UTF-8")
    create_database_spanish(output_database_path, intermediate_utf8_json_path)

if __name__ == "__main__":
    #create_ru_db_full("kaikki.org-dictionary-Russian.json")
    #create_es_db_full("kaikki.org-dictionary-Spanish_new.json")
    convert_file_to_utf8("kaikki.org-dictionary-English.json", "english_dict.json")