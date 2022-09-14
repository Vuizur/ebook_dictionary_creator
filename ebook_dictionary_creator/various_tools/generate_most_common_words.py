import sqlite3
import csv


def add_most_common_words_to_db(db_name: str, frequency_list_path: str):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    # cur.execute("""ALTER TABLE word ADD column 'frequency' INTEGER """)
    cur.execute("UPDATE word SET frequency = NULL")
    with open(frequency_list_path, "r", encoding="utf-8") as f:
        rd = csv.reader(f, delimiter="\t")
        for word, frequency in rd:

            res = cur.execute(
                "UPDATE word SET frequency = ? WHERE frequency IS NULL AND (word.word = ? OR word.word = ?)",
                (int(frequency), word, word.capitalize()),
            )
            # print(res.rowcount)
        cur.close()
        con.commit()
        con.close()


def get_most_common_words_from_DeReKo():
    with open(
        "DeReKo-2014-II-MainArchive-STT.100000.freq", encoding="utf-8"
    ) as f, open("common_nouns.txt", "w", encoding="utf-8") as out:
        rd = csv.reader(f, delimiter="\t")
        for line in rd:
            if len(line) == 4:
                word, base_form, POS, frequency = line
                if (POS == "NN" or POS == "NE") and word == base_form:
                    out.write(word + "\n")
