from stressed_cyrillic_tools import unaccentify


def remove_macrons_etc_from_latin(word: str):
    return (
        word.replace("ā", "a")
        .replace("ē", "e")
        .replace("ī", "i")
        .replace("ō", "o")
        .replace("ū", "u")
        .replace("Ā", "A")
        .replace("Ē", "E")
        .replace("Ī", "I")
        .replace("Ō", "O")
        .replace("Ū", "U")
        .replace("ă", "a")
        .replace("ĕ", "e")
        .replace("ĭ", "i")
        .replace("ŏ", "o")
        .replace("ŭ", "u")
        .replace("Ă", "A")
        .replace("Ĕ", "E")
        .replace("Ĭ", "I")
        .replace("Ŏ", "O")
        .replace("Ŭ", "U")
    )


def postprocess_inflections(
    language: str, word_and_inflections: list[str]
) -> list[str]:
    """Sometimes the Wiktionary data contains diacritics in their words that are actually not in texts
    and specify the pronunciation. This function adds versions of the words without these diacritics.

    The language should be passed as an English string (like "Latin" or "Russian")
    """

    word_and_all_inflections = []
    if language == "Latin":
        for word in word_and_inflections:
            word_and_all_inflections.append(word)
            word_and_all_inflections.append(remove_macrons_etc_from_latin(word))
    elif (
        language == "Russian"
        or language == "Ukrainian"
        or language == "Belarusian"
        or language == "Bulgarian"
        or language == "Serbian"
        or language == "Serbo-Croatian"
    ):
        for word in word_and_inflections:
            word_and_all_inflections.append(word)
            word_and_all_inflections.append(unaccentify(word))
    else:
        word_and_all_inflections = word_and_inflections

    # Remove duplicates while preserving order
    word_and_all_inflections = list(dict.fromkeys(word_and_all_inflections))

    return word_and_all_inflections


if __name__ == "__main__":
    print(remove_macrons_etc_from_latin("Themistō"))
