import json
import pandas as pd
import wordfreq


def load_sentences_from_tsv(tsv_file_path: str) -> pd.DataFrame:
    """
    Loads the sentences from the TSV file.
    """
    with open(tsv_file_path, "r", encoding="utf-8") as f:
        # Read tsv to pandas
        df = pd.read_csv(tsv_file_path, sep="\t", encoding="utf-8")

        df.columns = [
            "sentence_id",
            "sentence_source",
            "translated_sentence_id",
            "translated_sentence",
        ]
    return df


def create_word_occurence_dictionary(
    df: pd.DataFrame, tokenizer_lang="cs"
) -> dict[str, list[str]]:
    """
    Creates a dictionary that contains a list of example sentence IDS for each word
    """

    # Create a dictionary that contains a list of example sentence IDS for each word
    word_occurence_dictionary: dict[str, list[str]] = {}
    for index, row in df.iterrows():
        # Get the words using the wordfreq tokenizer
        words = wordfreq.tokenize(row["sentence_source"], tokenizer_lang)
        # words = row["sentence_source"].split(" ")
        # Add the sentence ID to the dictionary
        for word in words:
            if word not in word_occurence_dictionary:
                word_occurence_dictionary[word] = []
            word_occurence_dictionary[word].append(row["sentence_id"])
    return word_occurence_dictionary


def get_example_sentences_for_all_words_not_in_word_list(
    word_list: list,
    sentence_pairs_tsv_file_path: str,
) -> dict[str, list[tuple[str, str]]]:
    """
    Gets the example sentences for all words not in the word list.
    """
    sentences_df = load_sentences_from_tsv(sentence_pairs_tsv_file_path)
    # remove duplicate sentence_source fields
    sentences_df = sentences_df.drop_duplicates(subset="sentence_source")
    print(sentences_df)
    example_sentence_id_dict = create_word_occurence_dictionary(sentences_df)
    print(example_sentence_id_dict)
    new_unique_words_dict = {}
    # Iterate over example_sentence_id_dict and remove all words that are in the word list
    for word in example_sentence_id_dict:
        if word not in word_list:
            new_unique_words_dict[word] = example_sentence_id_dict[word]

    words_with_sentence_examples: dict[str, list[tuple[str, str]]] = {}
    for word in new_unique_words_dict:
        words_with_sentence_examples[word] = []
        for sentence_id in new_unique_words_dict[word]:
            # Get the source sentence and target sentence from the sentence ID
            source_sentence = sentences_df[sentences_df["sentence_id"] == sentence_id][
                "sentence_source"
            ].values[0]
            target_sentence = sentences_df[sentences_df["sentence_id"] == sentence_id][
                "translated_sentence"
            ].values[0]
            # sentence = sentences_df.loc[sentences_df["sentence_id"] == sentence_id]["sentence_source"].values[0]
            words_with_sentence_examples[word].append(
                (source_sentence, target_sentence)
            )
    return words_with_sentence_examples


def get_word_and_html_for_all_words_not_in_word_list(
    word_list: list, sentence_pairs_tsv_file_path: str
) -> dict[str, str]:
    """
    Gets the word and html for all words not in the word list.
    """
    words = get_example_sentences_for_all_words_not_in_word_list(
        word_list, sentence_pairs_tsv_file_path
    )
    word_and_html_dict = {}
    for word in words:
        word_and_html_dict[word] = ""
        counter = 0
        for sentence in words[word]:
            word_and_html_dict[word] += (
                "<p>" + sentence[0] + " - <i>" + sentence[1] + "</i>" "</p>"
            )
            counter += 1
            if counter > 4:
                break
    return word_and_html_dict


if __name__ == "__main__":
    example_sentences = get_example_sentences_for_all_words_not_in_word_list(
        [], "Sentence pairs in Czech-English - 2022-06-15.tsv"
    )

    # Print to JSON
    with open("example_sentences.json", "w", encoding="utf-8") as f:
        json.dump(example_sentences, f, ensure_ascii=False, indent=4)
    print("Done")
