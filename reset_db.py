import sqlite3

con = sqlite3.connect("words.db")
cur = con.cursor()