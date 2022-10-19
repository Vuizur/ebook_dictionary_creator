from sqlite3 import Cursor

from abc import ABC

# Unused code

class Language(ABC):
    language_string: str

    def delete_unneeded_entries():
        pass

    def add_additional_linkages():
        pass

    def link_up_alternative_forms(cur: Cursor):
        pass