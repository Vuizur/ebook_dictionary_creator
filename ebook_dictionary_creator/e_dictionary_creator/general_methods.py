from database_creator import convert_file_to_utf8, create_database_russian

# Deprecated

def create_ru_db_full(
    wiktextract_json_input_path,
    create_openrussian_db: bool,
    create_wiktionary_db=True,
    convert_utf8=True,
    openrussian_db_path="openrussian.db",
    output_database_path="russian_dict.db",
    intermediate_utf8_json_path="russian-dict.json",
):
    """Creates an SQLite database containing the data from Wiktextract combined with data by OpenRussian\n
    The Wiktextract data can be downloaded from kaikki.org"""
    if convert_utf8:
        convert_file_to_utf8(wiktextract_json_input_path, intermediate_utf8_json_path)
        print("Wiktextract file has been converted to UTF-8")
    # This creates the Wiktextract portion of the database
    if create_wiktionary_db:
        create_database_russian(output_database_path, intermediate_utf8_json_path)
        print("Wiktextract data has been added to database")
    # find_words_without_stress("russian_dict.db")

    if create_openrussian_db:
        create_openrussian_database(openrussian_db_path)
    add_openrussian_to_db_with_linkages(output_database_path, openrussian_db_path)
    print("OpenRussian data has been added to database")


def create_db_full(
    wiktextract_json_input_path: str,
    language: str,
    output_database_path: str,
    intermediate_utf8_json_path: str,
):
    convert_file_to_utf8(wiktextract_json_input_path, intermediate_utf8_json_path)
    print("File has been converted to UTF-8")
    create_database(output_database_path, intermediate_utf8_json_path, language)
