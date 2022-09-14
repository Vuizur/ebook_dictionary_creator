from pyglossary import Glossary
import sqlite3
import csv
import os

# TODO: Finish
DICT_CC_FOLDER = "dict_cc_es_de"


def add_es_de_to_database():
    con = sqlite3.connect("spanish_dict.db")
    cur = con.cursor()
    filename = os.listdir(DICT_CC_FOLDER)
    path = DICT_CC_FOLDER + "/" + filename[0]

    with open(path, "r", encoding="utf-8") as f:
        rd = csv.reader(f, delimiter="\t")
        counter = 0
        for row in rd:
            firstchar = row[0][0]
            if len(row) < 2 or firstchar == "#" or firstchar == "(" or firstchar == ".":
                continue
            else:
                headword = (
                    row[0]
                    .replace(" algo", " [")
                    .replace(" a-algn/algo", " [")
                    .replace(" a algn", " [")
                    .split(" [", 1)[0]
                )
                # these can also occur in the middle of words
                headword = headword.replace(" {f}", "").replace(" {m}", "")
                definition = row[1]
                definition = definition.replace(" {f}", "").replace(" {m}", "")
                pos = row[2]
                # This is difficult
                pos = pos.replace("adj adv", "adv")

                cur.execute()
            counter += 1
            print(row)
            if counter > 100:
                quit()


add_es_de_to_database()
