--CREATE TABLE pos
--(
--    pos_id INTEGER NOT NULL PRIMARY KEY,
--    name VARCHAR
--);
CREATE TABLE word 
(
    word_id INTEGER NOT NULL PRIMARY KEY,
    pos VARCHAR, --here had been pos_id
    canonical_form VARCHAR,
    alternative_canonical_form VARCHAR,
    romanized_form VARCHAR,
    genitive_form VARCHAR,
    adjective_form VARCHAR,
    nominative_plural_form VARCHAR,
    genitive_plural_form VARCHAR,
    ipa_pronunciation VARCHAR,
    lang VARCHAR,
    word VARCHAR,
    lang_code VARCHAR,
    word_lowercase VARCHAR,
    word_lower_and_without_yo VARCHAR
    --theoretically derived words could be added too
);

CREATE TABLE sense
(
    sense_id INTEGER NOT NULL PRIMARY KEY,
    word_id INTEGER NOT NULL,
    FOREIGN KEY(word_id) REFERENCES word(word_id)
);
CREATE TABLE form_of_word
(
    word_id INTEGER NOT NULL,
    base_word_id INTEGER NOT NULL,
    FOREIGN KEY(word_id) REFERENCES word(word_id),
    FOREIGN KEY(base_word_id) REFERENCES word(word_id)
    PRIMARY KEY(word_id, base_word_id)
);

--CREATE TABLE sense_tag
--(
--    --possibly: add categories/topics here
--    sense_tag_id INTEGER NOT NULL PRIMARY KEY,
--    name VARCHAR
--);
--CREATE TABLE sense_sense_tags
--(
--    sense_id INTEGER,
--    sense_tag_id INTEGER,
--    FOREIGN KEY(sense_id) REFERENCES sense(sense_id),
--    FOREIGN KEY(sense_tag_id) REFERENCES sense_tag(sense_tag_id)
--);
CREATE TABLE gloss
(
    gloss_id INTEGER NOT NULL PRIMARY KEY,
    sense_id INTEGER,
    gloss_string VARCHAR,
    word_case VARCHAR,
    FOREIGN KEY(sense_id) REFERENCES sense(sense_id)    
);