import json

def convert_json_file_to_utf8(file_path: str, output_file_path: str):
    with open(file_path, "r", encoding="utf-8") as f, \
            open(output_file_path, "w", encoding="utf-8") as out:
        for line in f:
            obj = json.loads(line)
            out.write(json.dumps(obj, ensure_ascii=False))


def compare_raw_extract_with_kaikki_json(raw_extract_path="D:/raw-wiktextract-data.json", kaikki_json_path="kaikki.org-dictionary-Russian.json", convert_utf8=False):
    utf_8_path_raw = "raw-wiktextract-data_utf8.json"
    utf_8_path_nonraw = "kaikki.org-dictionary-Russian_utf8.json"
    raw_path_only_russian = "raw-wiktextract-data_russian_new.json"

    if convert_utf8:

        # Convert both files to UTF-8
        #extract_russian_part(raw_extract_path, raw_path_only_russian)

        convert_json_file_to_utf8(raw_path_only_russian, utf_8_path_raw)
        convert_json_file_to_utf8(kaikki_json_path, utf_8_path_nonraw)

        # Extract russian words from raw extract

    # Compare the two files
    with open(utf_8_path_raw, "r", encoding="utf-8") as f1, \
            open(utf_8_path_raw, "r", encoding="utf-8") as f2:
        # Load both JSON lines files into memory
        json_lines_raw = [json.loads(line) for line in f1]
        json_lines_nonraw = [json.loads(line) for line in f2]

        for line_raw in json_lines_raw:
            # Check if word is in nonraw file
            if line_raw["word"] not in json_lines_nonraw:
                print(line_raw["word"])
                print("Not in nonraw file")
        
        for line_nonraw in json_lines_nonraw:
            # Check if word is in raw file
            if line_nonraw["word"] not in json_lines_raw:
                print(line_nonraw["word"])
                print("Not in raw file")




def extract_russian_part(raw_json_path: str, output_json_path: str):
    # with open("D:/raw-wiktextract-data.json", "r", encoding="utf-8") as f, \
    #     open("raw-wiktextract-data_russian_new.json", "w", encoding="utf-8") as out:
    with open(raw_json_path, "r", encoding="utf-8") as f, \
            open(output_json_path, "w", encoding="utf-8") as out:

        for line in f:
            obj = json.loads(line)
            if "lang" in obj and obj["lang"] == "Russian":
                out.write(line)


if __name__ == "__main__":
    compare_raw_extract_with_kaikki_json(convert_utf8=True)
