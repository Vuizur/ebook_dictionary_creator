# Ebook dictionary creator

This project has two goals:
1. The first is to create a performant database containing words and their definitions, including all inflections and proper linkages between them. This allows you to get the definition of a word regardless of the word's form. It currently uses En-Wiktionary data provided by Tatu Ylonen's Wiktextract project and the OpenRussian data (both under CC-BY-SA license). Cleaning up the data is language specific, and this has been done for Russian and Spanish so far
2. Based on this data, it wants to create high-quality dictionaries compatible with recent ebook readers. So far one [Spanish-English dictionary](spanish_dict.mobi/OEBPS/content.mobi) for Kindle has been created, and it works really well. Unfortunately the [kindle dictionary lookup algorithm](docs/stupid_kindle_algorithm.md) is horrible for non-English languages, which leads to some small mistakes that I will try to find a workaround for. But to my knowledge it is the best free Spanish-English kindle dictionary compared to the other I could find (and the paid ones are probably worse as well).

Contributions and feedback about words that are not displayed correctly in the Spanish-English Kindle dictionary are always welcome

### Acknowledgements
This project would not have been possible without the https://kaikki.org/ data provided by Tatu Ylonen, the OpenRussian data and the Pyglossary libary for the creation of the Kindle dictionary

### Similar projects

https://github.com/nyg/wiktionary-to-kindle apparently works very similarly, also supports inflections, as of now it only supports smaller languages though (has been tested for Finnish).

https://github.com/efskap/kindlewick  

https://github.com/BoboTiG/ebook-reader-dict is a program that parses the Wiktionary dump itself and outputs Kobo compatible files