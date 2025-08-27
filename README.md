# Ebook dictionary creator

You probably don't need to execute this code. If you are only looking for the dictionaries, download them [here](https://github.com/Vuizur/Wiktionary-Dictionaries)

<hr/>

This repo does two things:
1. The first is creating a performant database containing words and their definitions, including all inflections and proper linkages, using English Wiktionary data (and for Russian OpenRussian as well).
2. Based on this data, it creates high-quality dictionaries compatible with recent ebook readers. It uses an algorithm to fix bugs in the Kindle lookup engine for this that prevent inflections from being found - even official dictionaries suffer from it.

If you want another language or format, you can open an issue and I will take a look if I have time. I apologize that the code right now is somewhat messy.

Contributions and feedback about words that are not displayed correctly or unhelpful definitions (I tried to remove them all/link them to parent definitions) are always welcome. Additionally, you can tell me if the dictionary for your language is missing essential information.

### Example usage
You can install the package with `pip install git+https://github.com/Vuizur/ebook_dictionary_creator`

And then use it like this:

    from ebook_dictionary_creator import DictionaryCreator

    dict_creator = DictionaryCreator("Czech", "English")
    dict_creator.download_data_from_kaikki()
    dict_creator.create_database()
    dict_creator.export_to_tabfile()
    dict_creator.export_to_kindle(
        kindlegen_path="C:/Users/hanne/AppData/Local/Amazon/Kindle Previewer 3/lib/fc/bin/kindlegen.exe",
        try_to_fix_failed_inflections=False, # This tries to fix kindle's problems with inflections.
        # For example, if oso is in the dictionary as a headword, it will only display this headword, 
        # - if oso is the inflection of osar, osar will not be found. This tries to fix it. 
        # Currently only works for latin scripts.
        author="Vuizur",
        title="Czech to English dictionary",
        mobi_temp_folder_path="Czech-English-dict",
    )
    dict_creator.export_to_stardict("Vuizur", "Czech to English dictionary", "Czech-English-dict.ifo")  

### Installation and usage for beginners
1. Download and install [Python](https://www.python.org/) on your operating system
1. Open a terminal window and check if the installation was successful by typing ```python3 --version```. It should display something like 'Python 3.13.6'.
1. Download this repository. Click on the green <> Code button --> Download ZIP. Unzip it at a convenient location. If you are familiar with Git you can also clone the repository.
1. We need the executable 'kindlegen' in order to create .mobi files. The Amazon software '[Kindle Previewer]'(https://www.amazon.com/Kindle-Previewer/b?ie=UTF8&node=21381691011) needs to be installed on your computer to get it. 'kindlegen' is stored at the following location as of 2025:
   - macOS: '/Applications/Kindle Previewer 3.app/Contents/lib/fc/bin/kindlegen'
   - Windows: 'C:/Users/USERNAME/AppData/Local/Amazon/Kindle Previewer 3/lib/fc/bin/kindlegen.exe'
1. Open a terminal and change the directory to the unzipped repository created in 3. (```cd path/to/ebook_dictionary_creator```).
1. Download all necessary dependencies: ```pip install -e .```
1. Open the file 'create-dictionary.py' with a text editor and change **source** and **target language** and the **path to the 'kindlegen' executable** ('author', 'title' and 'mobi_temp_folder_path' are optional and do not have to be changed, if I am not mistaken):

```
from ebook_dictionary_creator import DictionaryCreator

dict_creator = DictionaryCreator("Malay", "English")#Source language, target language
dict_creator.download_data_from_kaikki()
dict_creator.create_database()
dict_creator.export_to_tabfile()
dict_creator.export_to_kindle(
    kindlegen_path="/Applications/Kindle Previewer 3.app/Contents/lib/fc/bin/kindlegen",# Path to kindlegen executable
    try_to_fix_failed_inflections=False,
    author="Vuizur",
    title="Malay to English dictionary",
    mobi_temp_folder_path="Malay-English-dict",
)
```
1. Execute the code by typing `python3 create-dictionary.py` into the terminal window
1. The file (e.g. 'Malay-English-dict.mobi') will be saved in the root folder (i.e. /ebook_dictionary_creator)


### Acknowledgements
This project would not have been possible without the https://kaikki.org/ data provided by Tatu Ylonen, the OpenRussian data and the Pyglossary library for the creation of the Kindle dictionary

### Similar projects

This project looks very good, but focuses more on DBnary translations (and doesn't seem to have inflections): https://github.com/karlb/wikdict-gen

https://github.com/nyg/wiktionary-to-kindle parses the Wiktionary itself. 

https://github.com/efskap/kindlewick apparently works very similarly, also supports inflections, as of now it only supports smaller languages though (has been tested for Finnish).

https://github.com/BoboTiG/ebook-reader-dict is a program that also parses the Wiktionary dump itself and outputs Kobo compatible files