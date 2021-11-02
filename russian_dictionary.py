import sqlite3
from typing import DefaultDict, Iterator
import itertools

class RussianDictionary:
    _con = sqlite3.connect("words2.db")
    _cur = _con.cursor()


    def get_dictionary_entry(self, word: str):
        results = self._cur.execute("""SELECT g.gloss_string, s.sense_id, base_forms.word_id, COALESCE(base_forms.canonical_form, base_forms.word) AS canonical_word FROM gloss g INNER JOIN
sense AS s ON g.sense_id = s.sense_id 
INNER JOIN
(SELECT --This query gets all base forms, the direct ones and the ones over the relation table
	word_id, word, canonical_form
FROM
	(
	SELECT
		w.word_id AS word_id,
		w.word AS word,
		w.canonical_form AS canonical_form
	FROM
		word w
	WHERE
		w.word = ?
		AND NOT EXISTS
	(
		SELECT
			fow.base_word_id
		FROM
			form_of_word fow
		WHERE
			fow.word_id = w.word_id)
UNION
	SELECT
		base_w.word_id AS word_id,
		base_w.word AS word,
		base_w.canonical_form AS canonical_form
	FROM
		word base_w
	JOIN form_of_word fow 
ON
		base_w.word_id = fow.base_word_id
	JOIN word der_w 
ON
		der_w.word_id = fow.word_id
	WHERE
		der_w.word = ?)) base_forms ON s.word_id = base_forms.word_id""", (word, word)).fetchall()
        if word[0].isupper() and len(results) == 0:
            return self.get_dictionary_entry(word.lower())

        res_dict = {}
        for gloss_string, sense_id, word_id, canonical_word in results:
            word_id = (canonical_word, word_id)
            if word_id not in res_dict:
                res_dict[word_id] = {}
            if sense_id not in res_dict[word_id]:
                res_dict[word_id][sense_id] = []
            res_dict[word_id][sense_id].append(gloss_string)
        
        fixed_dict = {k[0]:list(v.values()) for (k,v) in res_dict.items()}
            
        return fixed_dict

#dic = RussianDictionary()
#result = dic.get_dictionary_entry("облавы")
#print(result)