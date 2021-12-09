import csv, sqlite3, time


if __name__ == "__main__":

    conn = sqlite3.connect("openrussian_csv.db")


    dir = "openrussian-csvs"

    t = time.time()

    conn = sqlite3.connect("openrussian_csv_new.db" )
    cur = conn.cursor()
    adj_path = "openrussian-csvs/russian3 - adjectives.csv"
    conj_path = "openrussian-csvs/russian3 - conjugations.csv"
    decl_path = "openrussian-csvs/russian3 - declensions.csv"
    exp_w_path = "openrussian-csvs/russian3 - expressions_words.csv"
    noun_path = "openrussian-csvs/russian3 - nouns.csv"
    sent_w_path = "openrussian-csvs/russian3 - sentences_words.csv"
    sent_path = "openrussian-csvs/russian3 - sentences.csv"
    transl_path = "openrussian-csvs/russian3 - translations.csv"
    verb_path = "openrussian-csvs/russian3 - verbs.csv"
    word_f_path = "openrussian-csvs/russian3 - words_forms.csv"
    words_rels_path = "openrussian-csvs/russian3 - words_rels.csv"
    words_path = "openrussian-csvs/russian3 - words.csv"

    cur.execute("CREATE TABLE IF NOT EXISTS adjectives (word_id INTEGER,incomparable INTEGER,comparative VARCHAR,superlative VARCHAR,short_m VARCHAR,short_f VARCHAR,short_n VARCHAR,short_pl VARCHAR,decl_m_id INTEGER,decl_f_id INTEGER,decl_n_id INTEGER,decl_pl_id INTEGER)")

    with open(adj_path, encoding="utf-8") as adjectives:
        csvData = csv.reader(adjectives, delimiter=",")
        cur.execute('BEGIN TRANSACTION')
        print(next(csvData))

        for word_id,incomparable,comparative,superlative,short_m,short_f,short_n,short_pl,decl_m_id,decl_f_id,decl_n_id,decl_pl_id in csvData:
            cur.execute('INSERT OR IGNORE INTO adjectives (word_id,incomparable,comparative,superlative,short_m,short_f,short_n,short_pl,decl_m_id,decl_f_id,decl_n_id,decl_pl_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', 
            (word_id,incomparable,comparative,superlative,short_m,short_f,short_n,short_pl,decl_m_id,decl_f_id,decl_n_id,decl_pl_id))

        cur.execute('COMMIT')
        

    cur.execute("CREATE TABLE IF NOT EXISTS conjugations (id INTEGER,word_id INTEGER,sg1 VARCHAR,sg2 VARCHAR, sg3 VARCHAR, pl1 VARCHAR, pl2 VARCAR, pl3 VARCHAR)")
    with open(conj_path, encoding="utf-8") as conjugations:
        csvData = csv.reader(conjugations, delimiter=",")
        cur.execute('BEGIN TRANSACTION')
        print(next(csvData))

        for id,word_id,sg1,sg2,sg3,pl1,pl2,pl3 in csvData:
            cur.execute('INSERT OR IGNORE INTO conjugations (id,word_id,sg1,sg2,sg3,pl1,pl2,pl3) VALUES (?,?,?,?,?,?,?,?)', 
            (id,word_id,sg1,sg2,sg3,pl1,pl2,pl3))

        cur.execute('COMMIT')

    cur.execute("CREATE TABLE IF NOT EXISTS declensions (id INTEGER,word_id INTEGER,nom VARCHAR,gen VARCHAR, dat VARCHAR, acc VARCHAR, inst VARCAR, prep VARCHAR)")

    with open(decl_path, encoding="utf-8") as declensions:
        csvData = csv.reader(declensions, delimiter=",")
        cur.execute('BEGIN TRANSACTION')
        print(next(csvData))

        for id,word_id,nom,gen,dat,acc,inst,prep in csvData:
            cur.execute('INSERT OR IGNORE INTO declensions (id,word_id,nom,gen,dat,acc,inst,prep) VALUES (?,?,?,?,?,?,?,?)', 
            (id,word_id,nom,gen,dat,acc,inst,prep))

        cur.execute('COMMIT')
    
    cur.execute("CREATE TABLE IF NOT EXISTS expression_words (id INTEGER,expression_id INTEGER,referenced_word_id INTEGER, start INTEGER, length INTEGER)")

    with open(exp_w_path, encoding="utf-8") as expression_words:
        csvData = csv.reader(expression_words, delimiter=",")
        cur.execute('BEGIN TRANSACTION')
        print(next(csvData))

        for id,expression_id,referenced_word_id,start,length in csvData:
            cur.execute('INSERT OR IGNORE INTO expression_words (id,expression_id,referenced_word_id,start,length) VALUES (?,?,?,?,?)', 
            (id,expression_id,referenced_word_id,start,length))

        cur.execute('COMMIT')

    cur.execute("CREATE TABLE IF NOT EXISTS nouns (word_id INTEGER,gender TEXT,partner VARCHAR, animate INTEGER, indeclinable INTEGER, sg_only INTEGER, pl_only INTEGER, decl_sg_id INTEGER, decl_pl_id INTEGER)")

    with open(noun_path, encoding="utf-8") as nouns:
        csvData = csv.reader(nouns, delimiter=",")
        cur.execute('BEGIN TRANSACTION')
        print(next(csvData))

        for word_id,gender,partner,animate,indeclinable,sg_only,pl_only,decl_sg_id,decl_pl_id in csvData:
            cur.execute('INSERT OR IGNORE INTO nouns (word_id,gender,partner,animate,indeclinable,sg_only,pl_only,decl_sg_id,decl_pl_id) VALUES (?,?,?,?,?,?,?,?,?)', 
            (word_id,gender,partner,animate,indeclinable,sg_only,pl_only,decl_sg_id,decl_pl_id))

        cur.execute('COMMIT')

    cur.execute("CREATE TABLE IF NOT EXISTS sentences_words (id INTEGER,sentence_id INTEGER,word_id INTEGER, start INTEGER, length INTEGER)")

    with open(sent_w_path, encoding="utf-8") as sentences_words:
        csvData = csv.reader(sentences_words, delimiter=",")
        cur.execute('BEGIN TRANSACTION')
        print(next(csvData))

        for id,sentence_id,word_id,start,length in csvData:
            cur.execute('INSERT OR IGNORE INTO sentences_words (id,sentence_id,word_id,start,length) VALUES (?,?,?,?,?)', 
            (id,sentence_id,word_id,start,length))

        cur.execute('COMMIT')

    cur.execute("CREATE TABLE IF NOT EXISTS sentences (id INTEGER,ru VARCHAR,lang VARCHAR, tl VARCHAR, tatobae_key INTEGER, source_url VARCHAR, disabled INTEGER, locked INTEGER, level TEXT, audio_url VARCHAR, audio_attribution_url VARCHAR, audio_attribution_name VARCHAR)")

    with open(sent_path, encoding="utf-8") as sentences:
        csvData = csv.reader(sentences, delimiter=",")
        cur.execute('BEGIN TRANSACTION')
        print(next(csvData))

        for id,ru,lang, tl, tatobae_key, source_url, disabled, locked, level, audio_url, audio_attribution_url, audio_attribution_name in csvData:
            cur.execute('INSERT OR IGNORE INTO sentences (id,ru,lang, tl, tatobae_key, source_url, disabled, locked, level, audio_url, audio_attribution_url, audio_attribution_name) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', 
            (id,ru,lang, tl, tatobae_key, source_url, disabled, locked, level, audio_url, audio_attribution_url, audio_attribution_name))

        cur.execute('COMMIT')

    cur.execute("CREATE TABLE IF NOT EXISTS translations (id INTEGER,lang TEXT,word_id INTEGER, position INTEGER, tl VARCHAR, example_ru VARCHAR, example_tl VARCHAR, info VARCHAR)")

    with open(transl_path, encoding="utf-8") as translations:
        csvData = csv.reader(translations, delimiter=",")
        cur.execute('BEGIN TRANSACTION')
        print(next(csvData))

        for id,lang,word_id, position, tl, example_ru, example_tl, info in csvData:
            cur.execute('INSERT OR IGNORE INTO translations (id,lang,word_id, position, tl, example_ru, example_tl, info) VALUES (?,?,?,?,?,?,?,?)', 
            (id,lang,word_id, position, tl, example_ru, example_tl, info))

        cur.execute('COMMIT')

    cur.execute("CREATE TABLE IF NOT EXISTS verbs (word_id INTEGER, aspect TEXT, partner VARCHAR, imperative_sg VARCHAR, imperative_pl VARCHAR, past_m VARCHAR, past_f VARCHAR, past_n VARCHAR, past_pl VARCHAR, presfut_conj_id INTEGER, participle_active_present_id INTEGER,participle_active_past_id INTEGER,participle_passive_present_id INTEGER,participle_passive_past_id INTEGER)")

    with open(verb_path, encoding="utf-8") as verbs:
        csvData = csv.reader(verbs, delimiter=",")
        cur.execute('BEGIN TRANSACTION')
        print(next(csvData))

        for word_id, aspect, partner, imperative_sg, imperative_pl, past_m, past_f, past_n, past_pl, presfut_conj_id, participle_active_present_id,participle_active_past_id,participle_passive_present_id,participle_passive_past_id in csvData:
            cur.execute('INSERT OR IGNORE INTO verbs (word_id, aspect, partner, imperative_sg, imperative_pl, past_m, past_f, past_n, past_pl, presfut_conj_id, participle_active_present_id,participle_active_past_id,participle_passive_present_id,participle_passive_past_id ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (word_id, aspect, partner, imperative_sg, imperative_pl, past_m, past_f, past_n, past_pl, presfut_conj_id, participle_active_present_id,participle_active_past_id,participle_passive_present_id,participle_passive_past_id ))

        cur.execute('COMMIT')

    #TODO: words_forms left out because not in old database -> should be fixed

    cur.execute("CREATE TABLE IF NOT EXISTS words (id INTEGER, position INTEGER, bare VARCHAR, accented VARCHAR, derived_from_word_id INTEGER, rank INTEGER, disabled INTEGER, audio VARCHAR, usage_en TEXT, usage_de TEXT, number_value INTEGER, type TEXT, level TEXT)")

    with open(words_path, encoding="utf-8") as words:
        csvData = csv.reader(words, delimiter=",")
        cur.execute('BEGIN TRANSACTION')
        print(next(csvData))

        for id, position, bare, accented, derived_from_word_id, rank, disabled, audio, usage_en, usage_de, number_value, type, level in csvData:
            cur.execute('INSERT OR IGNORE INTO words (id, position, bare, accented, derived_from_word_id, rank, disabled, audio, usage_en, usage_de, number_value, type, level) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', 
            (id, position, bare, accented, derived_from_word_id, rank, disabled, audio, usage_en, usage_de, number_value, type, level))

        cur.execute('COMMIT')

    cur.execute("CREATE TABLE IF NOT EXISTS words_rels (id INTEGER, word_id INTEGER, rel_word_id INTEGER, relation TEXT)")

    with open(words_rels_path, encoding="utf-8") as words_rels:
        csvData = csv.reader(words_rels, delimiter=",")
        cur.execute('BEGIN TRANSACTION')
        print(next(csvData))

        for row in csvData:
            id, word_id, rel_word_id, relation = row
            cur.execute('INSERT OR IGNORE INTO words_rels (id, word_id, rel_word_id, relation) VALUES (?,?,?,?)', 
            (id, word_id, rel_word_id, relation))

        cur.execute('COMMIT')

    #TODO: INSERT INDICES
    #TODO: CHECK IF FIRST LINE IS INSERTED

    print("\n Time Taken: %.3f sec" % (time.time()-t))