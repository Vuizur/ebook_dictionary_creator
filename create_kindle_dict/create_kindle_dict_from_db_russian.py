from os import path
import sqlite3
from pyglossary.glossary import Glossary


STARTING_XHTML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xmlns:mbp="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf"  xmlns:idx="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf">

<head>
  <title>Русско-Английский Словарь</title>
</head>

<body>
  <mbp:frameset> """

ENDING_XHTML = """</mbp:frameset>
</body>
</html>"""

STARTING_OPF = """<?xml version='1.0' encoding='utf-8'?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="BookId">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:language>ru</dc:language>
    <dc:title>Русско-Английский Словарь</dc:title>
    <meta property="dcterms:modified">2021-10-08T21:21:57Z</meta>
    <dc:identifier id="BookId">urn:uuid:0acc8a4c-b4a0-4bab-8245-fe651899c367</dc:identifier>
    <x-metadata>
        <output encoding="utf-8"/>
        <DefaultLookupIndex>russian</DefaultLookupIndex>
        <DictionaryInLanguage>ru</DictionaryInLanguage>
        <DictionaryOutLanguage>en</DictionaryOutLanguage>
    </x-metadata>
  </metadata>
  <manifest>"""

MIDDLE_OPF = """<item id="sgc-nav.css" href="Styles/sgc-nav.css" media-type="text/css"/>
    <item id="nav.xhtml" href="Text/nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
  </manifest>
  <spine>"""

END_OPF = """<itemref idref="nav.xhtml" linear="no"/>
  </spine>
</package>"""

START_NAV = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="ru" xml:lang="ru">
<head>
  <title>ePub NAV</title>
  <meta charset="utf-8"/>
  <link href="../Styles/sgc-nav.css" rel="stylesheet" type="text/css"/>
</head>

<body epub:type="frontmatter">
  <nav epub:type="toc" id="toc" role="doc-toc"><h1>Оглавление</h1>

  <ol>"""

MIDDLE_NAV = """</ol></nav><nav epub:type="landmarks" id="landmarks" hidden=""><h1>Пометки</h1>

  <ol>
    <li><a epub:type="toc" href="#toc">Оглавление</a></li>"""

END_NAV = """</ol></nav>
</body>
</html>"""

CREATE_INFLECTION_TAGS_REGARDLESS = False


def create_kindle_dict_from_db(database_path):
    con = sqlite3.connect(database_path)
    cur = con.cursor()
    
    base_forms = cur.execute("SELECT w.word_id, w.canonical_form FROM word w WHERE w.word_id NOT IN (SELECT fow.word_id FROM form_of_word fow)").fetchall()
    base_forms_no_dupes = []
    #TODO: This removes meanings of words!
    already_used_forms = []
    for word_id, canonical_form in base_forms:
        if canonical_form in already_used_forms:
            continue
        else:
            base_forms_no_dupes.append((word_id, canonical_form))
            already_used_forms.append(canonical_form)

    base_forms = base_forms_no_dupes
    xhtmllist = []
    counter = 0
    for word_id, canonical_form in base_forms:
        counter = counter + 1
        xhtmllist.extend(["<idx:entry name=\"russian\" scriptable=\"yes\">\n<idx:short><a id=\"", str(counter), "\" />", "<idx:orth value = \"", canonical_form, "\"><b>", canonical_form, "</b>\n", ])

        #get inflections
        #TODO: get alternative canonical form as inflection as well
        #and add all unaccented versions as inflection as well

        inflections = cur.execute("""SELECT w1.canonical_form FROM word w1
JOIN form_of_word fow ON fow.word_id = w1.word_id 
JOIN word w2 ON w2.word_id = fow.base_word_id 
WHERE w2.canonical_form = ?""", (canonical_form,)).fetchall()

        if len(inflections) > 0 or CREATE_INFLECTION_TAGS_REGARDLESS:
            xhtmllist.append("<idx:infl>")

            for inflection in inflections:
                xhtmllist.extend(["<idx:iform value=\"", inflection[0], "\"></idx:iform>"])

            xhtmllist.append("</idx:infl>\n")
        
        xhtmllist.append("</idx:orth>")

        glosses = cur.execute("""SELECT g.gloss_string
FROM word w 
INNER JOIN sense s ON s.word_id = w.word_id 
INNER JOIN gloss g ON g.sense_id = s.sense_id 
WHERE w.canonical_form = ?""", (canonical_form,)).fetchall()

        for gloss in glosses:
            if gloss[0] == None: #This appears to happen for some reason
                continue
            xhtmllist.extend(["<p>", gloss[0],  "</p>"])

        if counter % 50000 == 0:
            print(counter)
        xhtmllist.append("</idx:short></idx:entry>\n")


    xhtmllist.append(ENDING_XHTML)

    #DEBUG part
    #with open("xhtmllist.txt", "w+", encoding="utf-8") as outf:
    #    for ln in xhtmllist:
    #        outf.write(ln + "\n")


    xhtml = "".join(xhtmllist)
    #with open("output_dictionary.xhtml", "w+", encoding="utf-8") as outdict:
    #    outdict.write(STARTING_XHTML)
    #    outdict.write(xhtml)
    #    outdict.write(ENDING_XHTML)

    
    manifest_opf = ""
    spine_opf = ""
    firstlist_nav_xhtml = ""
    secondlist_nav_xhtml = ""

    filenumber = 1
    linenumber =  0
    filename = "russian_dict_template/OEBPS/Text/" + "Section" + str(filenumber) + ".xhtml"
    f = open(filename, "w+", encoding="utf-8")
    f.write(STARTING_XHTML)
    manifest_opf +=  "<item id=\"" + "Section" + str(filenumber) + ".xhtml" + "\" href=\"Text/" + "Section" + str(filenumber) + ".xhtml" + "\" media-type=\"application/xhtml+xml\"/>\n"
    spine_opf += "<itemref idref=\"" + "Section" + str(filenumber) + ".xhtml" + "\"/>"
    firstlist_nav_xhtml += "<li><a href=\"" + "Section" + str(filenumber)+ ".xhtml" + "\">Русско-Английский Словарь</a></li>\n"
    secondlist_nav_xhtml += "<li><a epub:type=\"bodymatter\" href=\"" + "Section" + str(filenumber) + ".xhtml" + "\">Основной текст</a></li>\n"

    for line in xhtmllist:
        linenumber += 1
        if linenumber > 40000 and "<idx:entry name=\"russian\"" in line:
            f.write(ENDING_XHTML)
            f.close()
            filenumber += 1
            filename = "russian_dict_template/OEBPS/Text/" + "Section" + str(filenumber) + ".xhtml"
            f = open(filename, "w+", encoding="utf-8")
            manifest_opf +=  "<item id=\"" + "Section" + str(filenumber) + ".xhtml" + "\" href=\"Text/" + "Section" + str(filenumber) + ".xhtml" + "\" media-type=\"application/xhtml+xml\"/>\n"
            spine_opf += "<itemref idref=\"" + "Section" + str(filenumber) + ".xhtml" + "\"/>"
            firstlist_nav_xhtml += "<li><a href=\"" + "Section" + str(filenumber)+ ".xhtml" + "\">Русско-Английский Словарь</a></li>\n"
            secondlist_nav_xhtml += "<li><a epub:type=\"bodymatter\" href=\"" + "Section" + str(filenumber) + ".xhtml" + "\">Основной текст</a></li>\n"

            f.write(STARTING_XHTML)
            f.write(line)
            linenumber = 0
        else:
            f.write(line)
    f.write(ENDING_XHTML)
    f.close()

    with open("russian_dict_template/OEBPS/content.opf", "w+", encoding="utf-8") as opf_f:
        opf_f.write(STARTING_OPF)
        opf_f.write(manifest_opf)
        opf_f.write(MIDDLE_OPF)
        opf_f.write(spine_opf)
        opf_f.write(END_OPF)

    with open("russian_dict_template/OEBPS/Text/nav.xhtml", "w+", encoding="utf-8") as nav_f:
        nav_f.write(START_NAV)
        nav_f.write(firstlist_nav_xhtml)
        nav_f.write(MIDDLE_NAV)
        nav_f.write(secondlist_nav_xhtml)
        nav_f.write(END_NAV)
    #with open("output_dict.xhtml", "w", encoding="utf-8") as f:
    #    
    #    f.write(xhtml)

    cur.close()
    con.close()

def create_py_glossary_and_export(database_path, format="MOBI"):
    Glossary.init()
    glos = Glossary()

    defiFormat = "h"

    con = sqlite3.connect(database_path)
    cur = con.cursor()
    
    #base_forms = cur.execute("SELECT w.word_id, w.canonical_form FROM word w WHERE w.word_id NOT IN (SELECT fow.word_id FROM form_of_word fow)").fetchall()
    base_forms = cur.execute("""SELECT w.word_id, w.canonical_form FROM word w
WHERE w.word_id IN (SELECT sense.word_id FROM sense) GROUP BY w.canonical_form
""").fetchall()
    #base_forms_no_dupes = []
    ##TODO: This removes meanings of words!- Maybe?
    #already_used_forms = []
#
    #for word_id, canonical_form in base_forms:
    #    if canonical_form in already_used_forms:
    #        continue
    #    else:
    #        base_forms_no_dupes.append((word_id, canonical_form))
    #        already_used_forms.append(canonical_form)

    print(str(len(base_forms)) + " base forms")


    #base_forms = base_forms_no_dupes
    counter = 0
    for word_id, canonical_form in base_forms:
        counter = counter + 1
        
        #get inflections
        #TODO: get alternative canonical form as inflection as well
        #and add all unaccented versions as inflection as well

        inflections = cur.execute("""SELECT w1.canonical_form FROM word w1
JOIN form_of_word fow ON fow.word_id = w1.word_id 
JOIN word w2 ON w2.word_id = fow.base_word_id 
WHERE w2.canonical_form = ?""", (canonical_form,)).fetchall()

        infl_list = []

        for inflection in inflections:
            infl_list.append(inflection[0])
        infl_list = list(set(infl_list)) #TODO: Find out why there are duplicates here
        glosses = cur.execute("""SELECT g.gloss_string
FROM word w 
INNER JOIN sense s ON s.word_id = w.word_id 
INNER JOIN gloss g ON g.sense_id = s.sense_id 
WHERE w.canonical_form = ?""", (canonical_form,)).fetchall()

        glosses_list = []
        for gloss in glosses:
            if gloss[0] == None: #This appears to happen for some reason
                continue
            glosses_list.append(gloss[0])

        glosshtml = ""
        for gloss in glosses_list:
            glosshtml += "<p>" + gloss + "</p>"
        all_forms = [canonical_form]
        all_forms.extend(infl_list)
        glos.addEntryObj(glos.newEntry(all_forms, glosshtml, defiFormat))
        if counter % 2000 == 0:
            print(str(counter) + " words")
    glos.setInfo("title", "Russian-English Dictionary")
    glos.setInfo("author", "Vuizur")
    glos.sourceLangName = "Russian"
    glos.targetLangName = "English"
    #Spellcheck set to false because not supported for Russian
    if format == "MOBI":
        glos.write("test.mobi", format="Mobi", keep=True, exact= True, spellcheck=False, kindlegen_path="C:/Users/hanne/AppData/Local/Amazon/Kindle Previewer 3/lib/fc/bin/kindlegen.exe")
        #I don't know why the result does not work, I guess it is because of the combining accent symbol

    elif format == "STARDICT":
        glos.write("russian.ifo", format="Stardict")
    elif format == "TABFILE":
        glos.write("russian.txt", format="Tabfile")
