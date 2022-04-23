from create_databases.download_kaikki_db import download_kaikki_db
from main import create_ru_db_full


def update_russian_data():
    download_kaikki_db("Russian")
    create_ru_db_full("kaikki/kaikki.org-dictionary-Russian.json", create_wiktionary_db=True, create_openrussian_db=False, \
        convert_utf8=True)

if __name__ == "__main__":
    update_russian_data()