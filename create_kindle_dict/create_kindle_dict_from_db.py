import sqlite3

def create_kindle_dict_from_db():
    con = sqlite3.connect("words4.db")
    cur = con.cursor()

    base_forms = cur.execute("SELECT w.word_id, w.canonical_form FROM word w WHERE w.word_id NOT IN (SELECT fow.word_id FROM form_of_word fow)").fetchall()

    xhtmllist = ["""<html xmlns:math="http://exslt.org/math" xmlns:svg="http://www.w3.org/2000/svg" xmlns:tl="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf"

xmlns:saxon="http://saxon.sf.net/" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"

xmlns:cx="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf" xmlns:dc="http://purl.org/dc/elements/1.1/"

xmlns:mbp="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf" xmlns:mmc="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf" xmlns:idx="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf">

<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head>

<body>

<mbp:frameset>"""]
    counter = 0
    for word_id, canonical_form in base_forms:
        counter = counter + 1
        xhtmllist.extend(["<idx:entry name=\"russian\" scriptable=\"yes\" spell=\"yes\">\n\n<idx:orth>", canonical_form, "\n\n", "<idx:infl>"])

        #get inflections
        #get alternative canonical form as inflection as well
        #and add all unaccented versions as inflection as well

        inflections = cur.execute("""SELECT w1.canonical_form FROM word w1
JOIN form_of_word fow ON fow.word_id = w1.word_id 
JOIN word w2 ON w2.word_id = fow.base_word_id 
WHERE w2.canonical_form = ?""", (canonical_form,)).fetchall()

        for inflection in inflections:
            xhtmllist.extend(["<idx:iform value=\"", inflection[0], "\"></idx:iform>"])

        xhtmllist.append("</idx:infl>\n</idx:orth>")

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
        xhtmllist.append("</idx:entry>")


    xhtmllist.append("""</mbp:frameset>

    </body>

    </html>""")

    #DEBUG part
    with open("xhtmllist.txt", "w+", encoding="utf-8") as outf:
        for ln in xhtmllist:
            outf.write(ln + "\n")


    xhtml = "".join(xhtmllist)

    with open("output_dict.xhtml", "w", encoding="utf-8") as f:
        f.write(xhtml)


    cur.close()
    con.close()

if __name__ == "__main__":
    create_kindle_dict_from_db()