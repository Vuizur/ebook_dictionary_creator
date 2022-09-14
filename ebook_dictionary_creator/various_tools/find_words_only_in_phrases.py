import sqlite3


def find_words_only_in_phrases():
    con = sqlite3.connect("compiled_databases/Spanish_dict.db")
    cur = con.cursor()
    all_words = cur.execute(
        "SELECT word from word WHERE pos != 'name' GROUP BY word"
    ).fetchall()

    words_without_spaces = set()
    words_contained_in_phrases = set()
    word: str
    for (word,) in all_words:
        if " " in word:
            split_words = word.split()
            split_w_rem = []
            for word in split_words:
                if not word[0].isupper():
                    split_w_rem.append(word.replace(",", ""))
            words_contained_in_phrases.update(split_w_rem)
        else:
            words_without_spaces.add(word)

    words_only_contained_in_phrases = words_contained_in_phrases - words_without_spaces

    with open("words_only_in_phrases.txt", "w", encoding="utf-8") as out:
        for word in words_only_contained_in_phrases:
            out.write(word + "\n")

    cur.close()
    con.close()


if __name__ == "__main__":
    find_words_only_in_phrases()
