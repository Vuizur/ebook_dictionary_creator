from os import remove
import urllib.request

def download_kaikki_db(lang: str):
    lang = lang.capitalize()
    url_path = f"https://kaikki.org/dictionary/{lang}/kaikki.org-dictionary-{lang}.json"
    file_path = f"kaikki/kaikki.org-dictionary-{lang}.json"
    try:
        remove(file_path)
    except:
        pass
    urllib.request.urlretrieve(url_path, file_path)