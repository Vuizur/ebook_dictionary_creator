# Ebook dictionary creator

This project has two goals:
1. The first is to create a performant database containing words and their definitions, including all inflections and proper linkages between them. This allows you to get the definition of a word regardless of the word's case/tense. I will soon add an example explaining how you can use this as a fast dictionary with only one SQL query.
2. Based on this data, it creates high-quality dictionaries compatible with recent ebook readers. It uses an algorithm to fix bugs in the Kindle lookup engine for this that prevent inflections from being found - even official dictionaries suffer from it. Look in the releases section for already available dictionaries.
3. I will soon release the dictionaries as a Tabfile so that you can convert it to other formats as well

Contributions and feedback about words that are not displayed correctly or unhelpful definitions (I tried to remove them all/link them to parent definitions) are always welcome. Additionally, you can tell me if the dictionary for your language is missing essential information.
### Acknowledgements
This project would not have been possible without the https://kaikki.org/ data provided by Tatu Ylonen, the OpenRussian data and the Pyglossary library for the creation of the Kindle dictionary

### Similar projects

https://github.com/nyg/wiktionary-to-kindle 

https://github.com/efskap/kindlewick apparently works very similarly, also supports inflections, as of now it only supports smaller languages though (has been tested for Finnish).

https://github.com/BoboTiG/ebook-reader-dict is a program that parses the Wiktionary dump itself and outputs Kobo compatible files