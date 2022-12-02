import os
from pyglossary import Glossary

from ebook_dictionary_creator.e_dictionary_creator.dictionary_creator import convert_line_endings

#def fix_line_endings(ifo_file_path: str):
#    """Fixes the line endings, because KOReader/sdcv apparently doesn't like CRLF"""
#    # Convert line endings of IFO file to Unix
#    with open(ifo_file_path, 'rb') as f:
#        lines = f.readlines()
#    with open(ifo_file_path, 'wb') as f:
#        for line in lines:
#            f.write(line.replace(b'\r\n', b'\n'))

def convert_stardict_to_tabfile_and_back(stardict_path: str, output_path: str):
    """For some reasons this solves some bugs for sdcv/KOReader. But I don't know why yet.
    By default this takes an html dictionary and converts it to a tabfile and back to a stardict html dict."""
    Glossary.init()
    glos = Glossary()
    TEMP_FILE_NAME = "Temp90285q027fgd.txt"
    glos.convert(inputFilename=stardict_path, outputFilename=TEMP_FILE_NAME, outputFormat="Tabfile")
    glos.convert(inputFilename=TEMP_FILE_NAME, outputFilename=output_path, outputFormat="Stardict", writeOptions={"sametypesequence": "h"})
    convert_line_endings(output_path)
    # Delete the temporary file
    os.remove("Temp90285q027fgd.txt")