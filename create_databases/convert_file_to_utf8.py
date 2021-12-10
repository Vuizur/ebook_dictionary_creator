import json

FILENAME_IN = "kaikki.org-dictionary-Spanish_new.json"
FILENAME_OUT = "spanish-dict-utf8_new.json"

def convert_file_to_utf8(input_filename, output_filename):
    with open(input_filename, "r", encoding="utf-8") as input, \
        open(output_filename, "w", encoding="utf-8") as out:
        for line in input:
            data = json.loads(line) 
            json.dump(data, out, ensure_ascii=False)
            out.write("\n")
if __name__ == "__main__":
    convert_file_to_utf8(FILENAME_IN, FILENAME_OUT)
