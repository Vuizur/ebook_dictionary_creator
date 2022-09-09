import csv, sqlite3, time

import importlib.resources as pkg_resources
from ebook_dictionary_creator import data


def create_openrussian_database(openrussian_database_path):

    t = time.time()

    conn = sqlite3.connect(openrussian_database_path)
    cur = conn.cursor()
    adj_path = "russian3 - adjectives.csv"
    # Load with pkg_resources

    conj_path = "russian3 - conjugations.csv"
    decl_path = "russian3 - declensions.csv"
    exp_w_path = "russian3 - expressions_words.csv"
    noun_path = "russian3 - nouns.csv"
    sent_w_path = "russian3 - sentences_words.csv"
    sent_path = "russian3 - sentences.csv"
    transl_path = "russian3 - translations.csv"
    verb_path = "russian3 - verbs.csv"
    word_f_path = "russian3 - words_forms.csv"
    words_rels_path = "russian3 - words_rels.csv"
    words_path = "russian3 - words.csv"

    cur.execute(
        "CREATE TABLE IF NOT EXISTS adjectives (word_id INTEGER NOT NULL PRIMARY KEY,incomparable INTEGER,comparative VARCHAR,superlative VARCHAR,short_m VARCHAR,short_f VARCHAR,short_n VARCHAR,short_pl VARCHAR,decl_m_id INTEGER,decl_f_id INTEGER,decl_n_id INTEGER,decl_pl_id INTEGER)"
    )

    # with open(adj_path, encoding="utf-8") as adjectives:
    with pkg_resources.open_text(data, adj_path) as adjectives:
        csvData = csv.reader(adjectives, delimiter=",")
        cur.execute("BEGIN TRANSACTION")
        print(next(csvData))

        for (
            word_id,
            incomparable,
            comparative,
            superlative,
            short_m,
            short_f,
            short_n,
            short_pl,
            decl_m_id,
            decl_f_id,
            decl_n_id,
            decl_pl_id,
        ) in csvData:
            cur.execute(
                "INSERT OR IGNORE INTO adjectives (word_id,incomparable,comparative,superlative,short_m,short_f,short_n,short_pl,decl_m_id,decl_f_id,decl_n_id,decl_pl_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    word_id,
                    incomparable,
                    comparative,
                    superlative,
                    short_m,
                    short_f,
                    short_n,
                    short_pl,
                    decl_m_id,
                    decl_f_id,
                    decl_n_id,
                    decl_pl_id,
                ),
            )

        cur.execute("COMMIT")

    cur.execute(
        "CREATE TABLE IF NOT EXISTS conjugations (id INTEGER NOT NULL PRIMARY KEY,word_id INTEGER,sg1 VARCHAR,sg2 VARCHAR, sg3 VARCHAR, pl1 VARCHAR, pl2 VARCAR, pl3 VARCHAR)"
    )
    with pkg_resources.open_text(data, conj_path) as conjugations:
        csvData = csv.reader(conjugations, delimiter=",")
        cur.execute("BEGIN TRANSACTION")
        print(next(csvData))

        for id, word_id, sg1, sg2, sg3, pl1, pl2, pl3 in csvData:
            cur.execute(
                "INSERT OR IGNORE INTO conjugations (id,word_id,sg1,sg2,sg3,pl1,pl2,pl3) VALUES (?,?,?,?,?,?,?,?)",
                (id, word_id, sg1, sg2, sg3, pl1, pl2, pl3),
            )

        cur.execute("COMMIT")

    cur.execute(
        "CREATE TABLE IF NOT EXISTS declensions (id INTEGER NOR NULL PRIMARY KEY,word_id INTEGER,nom VARCHAR,gen VARCHAR, dat VARCHAR, acc VARCHAR, inst VARCAR, prep VARCHAR)"
    )

    with pkg_resources.open_text(data, decl_path) as declensions:
        csvData = csv.reader(declensions, delimiter=",")
        cur.execute("BEGIN TRANSACTION")
        print(next(csvData))

        for id, word_id, nom, gen, dat, acc, inst, prep in csvData:
            cur.execute(
                "INSERT OR IGNORE INTO declensions (id,word_id,nom,gen,dat,acc,inst,prep) VALUES (?,?,?,?,?,?,?,?)",
                (id, word_id, nom, gen, dat, acc, inst, prep),
            )

        cur.execute("COMMIT")

    cur.execute(
        "CREATE TABLE IF NOT EXISTS expression_words (id INTEGER NOT NULL PRIMARY KEY,expression_id INTEGER,referenced_word_id INTEGER, start INTEGER, length INTEGER)"
    )

    with pkg_resources.open_text(data, exp_w_path) as expression_words:
        csvData = csv.reader(expression_words, delimiter=",")
        cur.execute("BEGIN TRANSACTION")
        print(next(csvData))

        for id, expression_id, referenced_word_id, start, length in csvData:
            cur.execute(
                "INSERT OR IGNORE INTO expression_words (id,expression_id,referenced_word_id,start,length) VALUES (?,?,?,?,?)",
                (id, expression_id, referenced_word_id, start, length),
            )

        cur.execute("COMMIT")

    cur.execute(
        "CREATE TABLE IF NOT EXISTS nouns (word_id INTEGER NOT NULL PRIMARY KEY,gender TEXT,partner VARCHAR, animate INTEGER, indeclinable INTEGER, sg_only INTEGER, pl_only INTEGER, decl_sg_id INTEGER, decl_pl_id INTEGER)"
    )

    with pkg_resources.open_text(data, noun_path) as nouns:
        csvData = csv.reader(nouns, delimiter=",")
        cur.execute("BEGIN TRANSACTION")
        print(next(csvData))

        for (
            word_id,
            gender,
            partner,
            animate,
            indeclinable,
            sg_only,
            pl_only,
            decl_sg_id,
            decl_pl_id,
        ) in csvData:
            cur.execute(
                "INSERT OR IGNORE INTO nouns (word_id,gender,partner,animate,indeclinable,sg_only,pl_only,decl_sg_id,decl_pl_id) VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    word_id,
                    gender,
                    partner,
                    animate,
                    indeclinable,
                    sg_only,
                    pl_only,
                    decl_sg_id,
                    decl_pl_id,
                ),
            )

        cur.execute("COMMIT")

    cur.execute(
        "CREATE TABLE IF NOT EXISTS sentences_words (id INTEGER NOT NULL PRIMARY KEY,sentence_id INTEGER,word_id INTEGER, start INTEGER, length INTEGER)"
    )

    with pkg_resources.open_text(data, sent_w_path) as sentences_words:
        csvData = csv.reader(sentences_words, delimiter=",")
        cur.execute("BEGIN TRANSACTION")
        print(next(csvData))

        for id, sentence_id, word_id, start, length in csvData:
            cur.execute(
                "INSERT OR IGNORE INTO sentences_words (id,sentence_id,word_id,start,length) VALUES (?,?,?,?,?)",
                (id, sentence_id, word_id, start, length),
            )

        cur.execute("COMMIT")

    cur.execute(
        "CREATE TABLE IF NOT EXISTS sentences (id INTEGER NOT NULL PRIMARY KEY,ru VARCHAR,lang VARCHAR, tl VARCHAR, tatobae_key INTEGER, source_url VARCHAR, disabled INTEGER, locked INTEGER, level TEXT, audio_url VARCHAR, audio_attribution_url VARCHAR, audio_attribution_name VARCHAR)"
    )

    with pkg_resources.open_text(data, sent_path) as sentences:
        csvData = csv.reader(sentences, delimiter=",")
        cur.execute("BEGIN TRANSACTION")
        print(next(csvData))

        for (
            id,
            ru,
            lang,
            tl,
            tatobae_key,
            source_url,
            disabled,
            locked,
            level,
            audio_url,
            audio_attribution_url,
            audio_attribution_name,
        ) in csvData:
            cur.execute(
                "INSERT OR IGNORE INTO sentences (id,ru,lang, tl, tatobae_key, source_url, disabled, locked, level, audio_url, audio_attribution_url, audio_attribution_name) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    id,
                    ru,
                    lang,
                    tl,
                    tatobae_key,
                    source_url,
                    disabled,
                    locked,
                    level,
                    audio_url,
                    audio_attribution_url,
                    audio_attribution_name,
                ),
            )

        cur.execute("COMMIT")

    cur.execute(
        "CREATE TABLE IF NOT EXISTS translations (id INTEGER NOT NULL PRIMARY KEY,lang TEXT,word_id INTEGER, position INTEGER, tl VARCHAR, example_ru VARCHAR, example_tl VARCHAR, info VARCHAR)"
    )

    with pkg_resources.open_text(data, transl_path) as translations:
        csvData = csv.reader(translations, delimiter=",")
        cur.execute("BEGIN TRANSACTION")
        print(next(csvData))

        for id, lang, word_id, position, tl, example_ru, example_tl, info in csvData:
            cur.execute(
                "INSERT OR IGNORE INTO translations (id,lang,word_id, position, tl, example_ru, example_tl, info) VALUES (?,?,?,?,?,?,?,?)",
                (id, lang, word_id, position, tl, example_ru, example_tl, info),
            )

        cur.execute("COMMIT")

    cur.execute(
        "CREATE TABLE IF NOT EXISTS verbs (word_id INTEGER NOT NULL PRIMARY KEY, aspect TEXT, partner VARCHAR, imperative_sg VARCHAR, imperative_pl VARCHAR, past_m VARCHAR, past_f VARCHAR, past_n VARCHAR, past_pl VARCHAR, presfut_conj_id INTEGER, participle_active_present_id INTEGER,participle_active_past_id INTEGER,participle_passive_present_id INTEGER,participle_passive_past_id INTEGER)"
    )

    with pkg_resources.open_text(data, verb_path) as verbs:
        csvData = csv.reader(verbs, delimiter=",")
        cur.execute("BEGIN TRANSACTION")
        print(next(csvData))

        for (
            word_id,
            aspect,
            partner,
            imperative_sg,
            imperative_pl,
            past_m,
            past_f,
            past_n,
            past_pl,
            presfut_conj_id,
            participle_active_present_id,
            participle_active_past_id,
            participle_passive_present_id,
            participle_passive_past_id,
        ) in csvData:
            cur.execute(
                "INSERT OR IGNORE INTO verbs (word_id, aspect, partner, imperative_sg, imperative_pl, past_m, past_f, past_n, past_pl, presfut_conj_id, participle_active_present_id,participle_active_past_id,participle_passive_present_id,participle_passive_past_id ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    word_id,
                    aspect,
                    partner,
                    imperative_sg,
                    imperative_pl,
                    past_m,
                    past_f,
                    past_n,
                    past_pl,
                    presfut_conj_id,
                    participle_active_present_id,
                    participle_active_past_id,
                    participle_passive_present_id,
                    participle_passive_past_id,
                ),
            )

        cur.execute("COMMIT")

    # TODO: words_forms left out because not in old database -> should be fixed

    cur.execute(
        "CREATE TABLE IF NOT EXISTS words (id INTEGER NOT NULL PRIMARY KEY, position INTEGER, bare VARCHAR, accented VARCHAR, derived_from_word_id INTEGER, rank INTEGER, disabled INTEGER, usage_en TEXT, usage_de TEXT, number_value INTEGER, type TEXT, level TEXT, created_at TEXT)"
    )

    with pkg_resources.open_text(data, words_path) as words:
        csvData = csv.reader(words, delimiter=",")
        cur.execute("BEGIN TRANSACTION")
        print(next(csvData))
        # id,position,bare,accented,derived_from_word_id,rank,disabled,usage_en,usage_de,number_value,type,level,created_at
        for (
            id,
            position,
            bare,
            accented,
            derived_from_word_id,
            rank,
            disabled,
            usage_en,
            usage_de,
            number_value,
            type,
            level,
            created_at,
        ) in csvData:
            cur.execute(
                "INSERT OR IGNORE INTO words (id, position, bare, accented, derived_from_word_id, rank, disabled, usage_en, usage_de, number_value, type, level, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    id,
                    position,
                    bare,
                    accented,
                    derived_from_word_id,
                    rank,
                    disabled,
                    usage_en,
                    usage_de,
                    number_value,
                    type,
                    level,
                    created_at,
                ),
            )

        cur.execute("COMMIT")

    cur.execute(
        "CREATE TABLE IF NOT EXISTS words_rels (id INTEGER NOT NULL PRIMARY KEY, word_id INTEGER, rel_word_id INTEGER, relation TEXT)"
    )

    with pkg_resources.open_text(data, words_rels_path) as words_rels:
        csvData = csv.reader(words_rels, delimiter=",")
        cur.execute("BEGIN TRANSACTION")
        print(next(csvData))

        for row in csvData:
            id, word_id, rel_word_id, relation = row
            cur.execute(
                "INSERT OR IGNORE INTO words_rels (id, word_id, rel_word_id, relation) VALUES (?,?,?,?)",
                (id, word_id, rel_word_id, relation),
            )

        cur.execute("COMMIT")

    # TODO: CHECK IF FIRST LINE IS INSERTED

    cur.execute("CREATE INDEX translation_word_id_idx ON translations(word_id);")
    cur.execute("CREATE INDEX adjectives_word_id_idx ON adjectives(word_id);")
    cur.execute("CREATE INDEX declensions_word_id_idx ON declensions(word_id);")
    cur.execute("CREATE INDEX verbs_word_id_idx ON verbs(word_id);")
    cur.execute("CREATE INDEX conjugations_word_id_idx ON conjugations(word_id);")
    cur.execute(
        "CREATE INDEX participle_index ON verbs(participle_active_present_id, participle_active_past_id, participle_passive_present_id, participle_passive_past_id);"
    )

    conn.commit()
    cur.close()
    conn.close()
    print("\n Time Taken: %.3f sec" % (time.time() - t))
