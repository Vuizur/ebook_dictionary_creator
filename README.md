# Ebook dictionary creator

This repo does two things:
1. The first is creating a performant database containing words and their definitions, including all inflections and proper linkages, using English Wiktionary data (and for Russian OpenRussian as well).
2. Based on this data, it creates high-quality dictionaries compatible with recent ebook readers. It uses an algorithm to fix bugs in the Kindle lookup engine for this that prevent inflections from being found - even official dictionaries suffer from it. So far I have only created a Spanish dictionary for Kindle and a Russian Stardict dictionary (and some other untested languages).

If you want another language or format, you can open an issue and I will take a look if I have time.

Contributions and feedback about words that are not displayed correctly or unhelpful definitions (I tried to remove them all/link them to parent definitions) are always welcome. Additionally, you can tell me if the dictionary for your language is missing essential information.

### Available languages (see in releases):
* Spanish
* German
* Swedish
* Russian (not for kindle, but for Stardict)

### Acknowledgements
This project would not have been possible without the https://kaikki.org/ data provided by Tatu Ylonen, the OpenRussian data and the Pyglossary library for the creation of the Kindle dictionary

### Similar projects

https://github.com/nyg/wiktionary-to-kindle parses the Wiktionary itself. 

https://github.com/efskap/kindlewick apparently works very similarly, also supports inflections, as of now it only supports smaller languages though (has been tested for Finnish).

https://github.com/BoboTiG/ebook-reader-dict is a program that also parses the Wiktionary dump itself and outputs Kobo compatible files
