import json


def convert_file_to_utf8(input_filename, output_filename):
    with open(input_filename, "r", encoding="utf-8") as input, open(
        output_filename, "w", encoding="utf-8"
    ) as out:
        for line in input:
            data = json.loads(line)
            json.dump(data, out, ensure_ascii=False)
            out.write("\n")


def compare_raw_extract_with_kaikki_json(
    raw_extract_path="D:/raw-wiktextract-data.json",
    kaikki_json_path="kaikki.org-dictionary-Russian.json",
    convert_utf8=False,
):
    utf_8_path_raw = "raw-wiktextract-data_utf8.json"
    utf_8_path_nonraw = "kaikki.org-dictionary-Russian_utf8.json"
    raw_path_only_russian = "raw-wiktextract-data_russian_new.json"

    if convert_utf8:

        # Convert both files to UTF-8
        # extract_russian_part(raw_extract_path, raw_path_only_russian)

        # convert_json_file_to_utf8(raw_path_only_russian, utf_8_path_raw)
        # utf_8_path_raw = raw_path_only_russian
        convert_file_to_utf8(kaikki_json_path, utf_8_path_nonraw)

        # Extract russian words from raw extract
    utf_8_path_raw = raw_path_only_russian

    # Compare the two files
    with open(utf_8_path_raw, "r", encoding="utf-8") as f1, open(
        utf_8_path_nonraw, "r", encoding="utf-8"
    ) as f2:
        # Load both JSON lines files into memory
        json_lines_raw = [json.loads(line) for line in f1]
        # Create a set of all the words in the raw extract
        words_raw = set([word["word"] for word in json_lines_raw])

        json_lines_nonraw = [json.loads(line) for line in f2]
        # Create a set of all the words in the non-raw extract
        words_nonraw = set([word["word"] for word in json_lines_nonraw])

        # Find the words that are only in the raw extract
        words_only_raw = words_raw - words_nonraw
        # Find the words that are only in the non-raw extract
        words_only_nonraw = words_nonraw - words_raw
        # Print results
        print("Words only in raw extract:")
        for word in words_only_raw:
            print(word)
        print("Words only in non-raw extract:")
        for word in words_only_nonraw:
            print(word)

        # for line_raw in json_lines_raw:
        #    # Check if word is in nonraw file
        #    if line_raw["word"] not in json_lines_nonraw:
        #        print(line_raw["word"])
        #        print("Not in nonraw file")
        #
        # for line_nonraw in json_lines_nonraw:
        #    # Check if word is in raw file
        #    if line_nonraw["word"] not in json_lines_raw:
        #        print(line_nonraw["word"])
        #        print("Not in raw file")


#


def extract_russian_part(raw_json_path: str, output_json_path: str):
    # with open("D:/raw-wiktextract-data.json", "r", encoding="utf-8") as f, \
    #     open("raw-wiktextract-data_russian_new.json", "w", encoding="utf-8") as out:
    with open(raw_json_path, "r", encoding="utf-8") as f, open(
        output_json_path, "w", encoding="utf-8"
    ) as out:

        for line in f:
            obj = json.loads(line)
            if "lang" in obj and obj["lang"] == "Russian":
                out.write(line)


if __name__ == "__main__":
    compare_raw_extract_with_kaikki_json(convert_utf8=True)
