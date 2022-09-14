from tatoebatools import ParallelCorpus
import pycountry
import wordfreq


class TatoebaAugmenter:
    def get_language_code(self, language: str):
        return pycountry.languages.get(name=language).alpha_3

    # Constructor takes the source language and target language and the path to the dictionary database
    def __init__(
        self,
        source_language: str,
        target_language: str,
        exception_word_list: set[str] = [],
    ):
        self.source_language = source_language
        self.target_language = target_language
        self.exception_word_list = exception_word_list
        # self.database_path = database_path

        # convert the full language string like "Spanish" to an ISO 639-1 code like "es"
        source_language_code = self.get_language_code(source_language)
        target_language_code = self.get_language_code(target_language)

        self.parallel_corpus = ParallelCorpus(
            source_language_code, target_language_code
        )
        self.create_word_occurence_dictionary()

    def create_word_occurence_dictionary(self):
        print("Creating word occurence dictionary...")
        # Create a dictionary that contains a list of example sentence IDS for each word
        self.word_occurence_dictionary: dict[str, list[str]] = {}
        for sentence, _ in self.parallel_corpus:
            # Get the words using the wordfreq tokenizer
            words = wordfreq.tokenize(
                sentence.text, self.get_language_code(self.source_language)
            )
            # words = row["sentence_source"].split(" ")
            # Add the sentence ID to the dictionary
            for word in words:
                if word not in self.word_occurence_dictionary:
                    self.word_occurence_dictionary[word] = []
                self.word_occurence_dictionary[word].append(sentence.sentence_id)

    def get_example_sentences_for_all_words_not_in_word_list(
        self,
    ) -> dict[str, list[tuple[str, str]]]:
        """
        Gets the example sentences for all words not in the word list.
        """

        new_unique_words_dict: dict[str, list[str]] = {}
        # Iterate over example_sentence_id_dict and remove all words that are in the word list
        for word in self.word_occurence_dictionary:
            if word not in self.exception_word_list:
                new_unique_words_dict[word] = self.word_occurence_dictionary[word]

        words_with_sentence_examples: dict[str, list[tuple[str, str]]] = {}
        df = self.parallel_corpus.dataframe
        df = df.drop_duplicates(subset="text_sentence")

        print("Getting example sentences for all words not in the word list...")
        for word in new_unique_words_dict.keys():
            words_with_sentence_examples[word] = []

            for sentence_id in new_unique_words_dict[word]:
                # Delete duplicates of row "text_sentence"
                # Get the row that has the index equal to the sentence ID using query
                row = df.query(f"sentence_id == {sentence_id}")  # .iloc[0]
                # row = df.loc[df["sentence_id"] == sentence_id]

                # Get the text_sentence and text_translation
                text_sentence = row["text_sentence"].values[0]
                text_translation = row["text_translation"].values[0]

                words_with_sentence_examples[word].append(
                    (text_sentence, text_translation)
                )
                # Print a message every 5000 sentences
                if len(words_with_sentence_examples[word]) % 5000 == 0:
                    print(
                        f"{len(words_with_sentence_examples[word])} sentences have been processed."
                    )

        return words_with_sentence_examples

    def get_word_and_html_for_all_words_not_in_word_list(self) -> dict[str, str]:
        """
        Gets the word and html for all words not in the word list.
        """

        words = self.get_example_sentences_for_all_words_not_in_word_list()
        print("Getting word and html for all words not in the word list...")
        word_and_html_dict = {}
        for word in words:
            word_and_html_dict[word] = ""
            counter = 0
            sentences = words[word]
            # Order sentences by the length of the first sentence, ascending
            sentences = sorted(sentences, key=lambda x: len(x[0]))
            for sentence in sentences:
                word_and_html_dict[word] += (
                    "<p>" + sentence[0] + " - <i>" + sentence[1] + "</i>" "</p>"
                )
                counter += 1
                if counter > 4:
                    break
        return word_and_html_dict

    def test(self):
        print(self.parallel_corpus.dataframe)
        # Write dataframe to tsv file
        self.parallel_corpus.dataframe.to_csv("test.tsv", sep="\t")


if __name__ == "__main__":
    ta = TatoebaAugmenter("Czech", "English")
    # df = ta.parallel_corpus.dataframe
    # df.query
    # print(df)
    # test = df.query("sentence_id == 338223")
    # print(test)

    # quit()
    # ta.test()

    dictionary = ta.get_word_and_html_for_all_words_not_in_word_list()
    # Print dictionary to txt
    with open("test.txt", "w", encoding="utf-8") as f:
        for word in dictionary:
            f.write(word + "\n")
            f.write(dictionary[word] + "\n")
            f.write("\n")
