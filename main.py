from create_databases.create_database_russian import create_database_russian
from create_databases.convert_file_to_utf8 import convert_file_to_utf8

def create_ru_db_full(output_database_path, wiktextract_json_input_path, intermediate_utf8_json_path="russian-dict.json"):
    """Creates an SQLite database containing the data from Wiktextract combined with data by OpenRussian\n
    The Wiktextract data can be downloaded from kaikki.org"""
    convert_file_to_utf8(wiktextract_json_input_path, intermediate_utf8_json_path)
    print("File has been converted to UTF-8")
    create_database_russian(output_database_path, intermediate_utf8_json_path)

def create_es_db_full(output_database_path, wiktextract_json_input_path, intermediate_utf8_json_path="spanish-dict.json"):
    convert_file_to_utf8(wiktextract_json_input_path, intermediate_utf8_json_path)
    create_database_russian(output_database_path, intermediate_utf8_json_path)

if __name__ == "__main__":
    create_ru_db_full("russian_dict.db", "kaikki.org-dictionary-Russian.json")