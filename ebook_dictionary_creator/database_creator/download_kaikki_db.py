from os import remove
import urllib.request
import os
import requests

# https://stackoverflow.com/questions/56950987/download-file-from-url-and-save-it-in-a-folder-python


def download(url: str, dest_folder: str):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # create folder if it does not exist

    filename = url.split("/")[-1].replace(" ", "_")  # be careful with file names
    file_path = os.path.join(dest_folder, filename)

    r = requests.get(url, stream=True)
    if r.ok:
        print("saving to", os.path.abspath(file_path))
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:  # HTTP status code 4XX/5XX
        print("Download failed: status code {}\n{}".format(r.status_code, r.text))


def download_kaikki_db(lang: str):
    lang = lang.capitalize()
    url_path = f"https://kaikki.org/dictionary/{lang}/kaikki.org-dictionary-{lang}.json"
    file_path = f"kaikki/kaikki.org-dictionary-{lang}.json"
    folder_path = "kaikki"
    try:
        remove(file_path)
    except:
        pass
    download(url_path, folder_path)
    print("Download finished!")
    # ret = urllib.request.urlretrieve(url_path, file_path)
    # print(ret)
