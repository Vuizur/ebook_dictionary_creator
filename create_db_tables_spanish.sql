CREATE TABLE word 
(
    word_id INTEGER NOT NULL PRIMARY KEY,
    pos VARCHAR,
    word VARCHAR,
    lang_code VARCHAR
    P
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
CREATE TABLE gloss
(
    gloss_id INTEGER NOT NULL PRIMARY KEY,
    sense_id INTEGER,
    gloss_string VARCHAR,
    FOREIGN KEY(sense_id) REFERENCES sense(sense_id)
);