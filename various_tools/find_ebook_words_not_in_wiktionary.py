#Copied from my add-stress-to-epub project
from shutil import rmtree
from spacy import load
from zipfile import ZipFile
from os import path, walk
from bs4 import BeautifulSoup
import sqlite3

extract_dir = "extract_dir_9580"
def find_words_not_in_ebook(input_file_path, language: str):
    """Outputs a tsv file containing the most common words that are not in the database"""
    if language == "Spanish":
        nlp = load("es_core_news_sm")
    elif language == "Russian":
        nlp = load("ru_core_news_sm")
    else:
        print("Language not supported")
        quit()
    
    nlp.disable_pipes("tok2vec", "morphologizer", "parser", "attribute_ruler", "lemmatizer", "ner")

    with ZipFile(input_file_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
    
    word_histogram = dict()
    if language == "Spanish":
        conn = sqlite3.connect("compiled_databases/Spanish_dict.db")
    elif language == "Russian":
        conn = sqlite3.connect("russian_dict.db")
    cur = conn.cursor()

    for subdir, dirs, files in walk("extract_dir_9580"):
        for file in files:
            filepath = path.join(subdir, file)
            if filepath.endswith(".xhtml"): 
                print(filepath)
                with open(filepath, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f.read(), "lxml")
                    for text_object in soup.find_all(text=True):
                        text: str = text_object.text
                        if len(text) > 0:
                            doc = nlp(text)

                            for token in doc:
                                if not any(c.isalpha() for c in token.text):
                                    continue
                                token = token.text.lower()
                                if language == "Russian":
                                    res = cur.execute("SELECT word FROM word WHERE word_lowercase = ?", (token,)).fetchone()
                                    if res == None:
                                        res = cur.execute("SELECT word FROM word WHERE word_lower_and_without_yo = ?", (token,)).fetchone()
                                else:
                                    #This has the problem that abbreviations like FBI don't get found! 
                                    res = cur.execute("SELECT word FROM word WHERE word = ?", (token,)).fetchone()
                                    if res == None:
                                        res = cur.execute("SELECT word FROM word WHERE word = ?", (token.capitalize,)).fetchone()
                                if res == None:
                                    if token not in word_histogram:
                                        word_histogram[token] = 1
                                    else:
                                        word_histogram[token] = word_histogram[token] + 1
    rmtree(extract_dir)
    word_histogram = dict((sorted(word_histogram.items(), key=lambda item: item[1], reverse=True)))

    with open("results.tsv", "w", encoding="utf-8") as f:
        
        for word, count in word_histogram.items():
            f.write(word + "\t" + str(count) + "\n")
        

                                    
if __name__ == "__main__":
    find_words_not_in_ebook("Noch' v bashnie uzhasa - Robiert Louriens Stain.epub", "Russian")