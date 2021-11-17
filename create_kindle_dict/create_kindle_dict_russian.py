import json
import sqlite3
import time
import os


def append_form_to_record(form: dict, form_dict:dict):
    form_tags = form["tags"]
    word_form = form["form"]
    if len(form_tags) == 1:
        if form_tags[0] == "canonical":
            form_dict["canonical_form"] = word_form
        elif form_tags[0] == "romanization":
            form_dict["romanized_form"] = word_form
        elif form_tags[0] == "genitive":
            form_dict["genitive_form"] = word_form
        elif form_tags[0] == "adjective":
            form_dict["adjective_form"] = word_form
        else:
            pass
            #print("unknown form")
            #print(form_tags[0])
    elif len(form_tags) == 2:
        if "nominative" in form_tags and "plural" in form_tags:
            form_dict["nominative_plural_form"] = word_form
        elif "genitive" in form_tags and "plural" in form_tags:
            form_dict["genitive_plural_form"] = word_form
        else:
            pass
            #print("unknown form with 2 tags:")
            #print(form_tags)
    else:
        pass
        #print("unknown form with strange number of tags:")
        #print(form_tags)

class Word:
    def __init__(self) -> None:
        self.word: str = ""
        self.inflected_forms: list[str] = []
        self.glosses: list[str] = []
class WordList:
    def __init__(self) -> None:
        #self.words: list[Word] = []
        #word - inflected_forms - glosses
        self.worddict: dict[str, (list[str], list[str])] = {}
    def add_inflected_form(self, inflected_form, base_word):
        if base_word in self.worddict:
            self.worddict[base_word][0].append(inflected_form)
        else:
            self.worddict[base_word] = ([inflected_form], [])
        #word_already_in_dict = False
        #for word in self.words:
        #    if word.word == base_word:
        #        word_already_in_dict = True
        #        word.inflected_forms.append(inflected_form)
        #        return
        #if(not word_already_in_dict):
        #    word_to_add = Word()
        #    word_to_add.word = base_word
        #    word_to_add.inflected_forms = [inflected_form]
        #    self.words.append(word_to_add)
    def add_gloss(self, base_word, gloss):
        if base_word in self.worddict:
            self.worddict[base_word][1].append(gloss)
        else:
            self.worddict[base_word] = ([], [gloss])
        #word_already_in_dict = False
        #for word in self.words:
        #    if word.word == base_word:
        #        word_already_in_dict = True
        #        word.glosses.append(gloss)
        #        return
        #if(not word_already_in_dict):
        #    word_to_add = Word()
        #    word_to_add.word = base_word
        #    word_to_add.glosses = [gloss]
        #    self.words.append(word_to_add)



word_list = WordList()
with open("russian-dict-utf8_3.json", "r", encoding="utf-8") as f:
                                #word_id, base_word_string
    form_of_words_to_add_later: "list[tuple(int, str)]" = []
    counter = 0
    for line in f:
        counter = counter + 1
        obj = json.loads(line)
        
        word = obj["word"]
        form_dict = {
        "canonical_form": None,
        "romanized_form": None,
        "genitive_form": None,
        "adjective_form": None,
        "nominative_plural_form": None,
        "genitive_plural_form": None
        }
        try:
            for form in obj["forms"]:
                append_form_to_record(form, form_dict)
        except:
            #print("Error for word")
            pass
        if form_dict["canonical_form"] != None:
            word = form_dict["canonical_form"]
            
        for sense in obj["senses"]:
            if "form_of" in sense:
                for base_word in sense["form_of"]:
                    word_list.add_inflected_form(word, base_word["word"])
                #todo: fix for glosses that aren't the base word (pretty rare case)
            else:
                try:
                    for gloss in sense["glosses"]:
                        word_list.add_gloss(word, gloss)
                except:
                    pass
        if (counter % 50000) == 0:
            print(counter)
#now generate xhtml

xhtmllist = ["""<html xmlns:math="http://exslt.org/math" xmlns:svg="http://www.w3.org/2000/svg" xmlns:tl="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf"

xmlns:saxon="http://saxon.sf.net/" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"

xmlns:cx="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf" xmlns:dc="http://purl.org/dc/elements/1.1/"

xmlns:mbp="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf" xmlns:mmc="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf" xmlns:idx="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf">

<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head>

<body>

<mbp:frameset>"""]
counter = 0
for dict_word, values in word_list.worddict.items():
    counter = counter + 1
    xhtmllist.extend(["<idx:entry name=\"russian\" scriptable=\"yes\" spell=\"yes\">\n\n<idx:orth>", dict_word, "\n\n", "<idx:infl>"])

    for inflection in values[0]:
        xhtmllist.extend(["<idx:iform value=\"", inflection, "\"></idx:iform>"])

    xhtmllist.append("</idx:infl>\n</idx:orth>")

    for gloss in values[1]:
        xhtmllist.extend(["<p>", gloss,  "</p>"])

    if counter % 50000 == 0:
        print(counter)
    xhtmllist.append("</idx:entry>")


xhtmllist.append("""</mbp:frameset>

</body>

</html>""")
xhtml = "".join(xhtmllist)

with open("output_dict.xhtml", "w", encoding="utf-8") as f:
    f.write(xhtml)


#for dict_word in word_list.words:
#    counter = counter + 1
#    xhtml = xhtml + "<idx:entry name=\"spanish\" scriptable=\"yes\" spell=\"yes\">\n\n<idx:orth>" + dict_word.word + "\n\n" + "<idx:infl>"
#
#    for inflection in dict_word.inflected_forms:
#        xhtml = xhtml + "<idx:iform value=\"" + inflection + "\"></idx:iform>"
#
#    xhtml = xhtml + "</idx:infl>" +"\n" "</idx:orth>"
#
#
#    for gloss in dict_word.glosses:
#        xhtml = xhtml + "<p>" + gloss +  "</p>"
#
#    if counter % 50000 == 0:
#        print(counter)
#    xhtml = xhtml + "</idx:entry>"
#
#
#xhtml = xhtml + """</mbp:frameset>
#
#</body>
#
#</html>"""
#
#with open("output_dict.xhtml", "w", encoding="utf-8") as f:
#    f.write(xhtml)
#