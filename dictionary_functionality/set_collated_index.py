import sqlite3

def set_nocase_collated_index(database_name: str):
    """This is necessary because SQLITE does not support UTF8 collations by default"""
    con = sqlite3.connect("")