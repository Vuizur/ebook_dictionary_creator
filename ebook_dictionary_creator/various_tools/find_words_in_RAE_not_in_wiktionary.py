import sqlite3


def find_RAE_words_not_in_Wiktionary():
    with open("diccionario-rae-completo.txt", encoding="utf-8") as f, open(
        "words_in_RAE_not_in_Wiktionary.txt", "w", encoding="utf-8"
    ) as out:
        conn = sqlite3.connect("compiled_databases/Spanish_dict.db")

        for l in f.readlines():
            res = conn.execute(
                "SELECT word FROM word WHERE word = ? OR word = ? OR word = ?",
                (l.lower().strip(), l.capitalize().strip(), l.upper().strip()),
            ).fetchone()
            if res == None:
                out.write(l)


def order_RAE_words_not_in_Wiktionary():
    with open("words_in_RAE_not_in_Wiktionary.txt", encoding="utf-8") as input, open(
        "CREA_total.txt", encoding="utf-8"
    ) as sorted_input:
        missing_words_alphabet_sort = []
        missing_words_alphabet_sort_lower = []
        for word in input.readlines():
            missing_words_alphabet_sort.append(word.strip())
            missing_words_alphabet_sort_lower.append(word.lower().strip())
        RAE_words_frequency = []
        sorted_input.readline()
        for line in sorted_input.readlines():
            index, word, freqabs, freqnorm = line.split()
            RAE_words_frequency.append(word)
    with open(
        "words_in_RAE_not_in_Wiktionary_sorted.txt", "w", encoding="utf-8"
    ) as sorted_RAE:
        finalized_ordered_words = []
        for word in RAE_words_frequency:
            try:
                index_of_word = missing_words_alphabet_sort_lower.index(word)
                finalized_ordered_words.append(
                    missing_words_alphabet_sort[index_of_word]
                )
                missing_words_alphabet_sort.pop(index_of_word)
                missing_words_alphabet_sort_lower.pop(index_of_word)
            except ValueError:
                pass

        finalized_ordered_words.extend(missing_words_alphabet_sort)
        for word in finalized_ordered_words:
            sorted_RAE.write(word + "\n")
