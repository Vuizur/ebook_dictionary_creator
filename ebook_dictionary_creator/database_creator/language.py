from sqlite3 import Cursor
from tarfile import LENGTH_LINK
from create_databases.create_database import (
    delete_unneeded_entries,
    link_up_alternative_forms_or_spellings,
)


from abc import ABC, abstractmethod


class Language(ABC):
    language_string: str

    def delete_unneeded_entries():
        pass

    def add_additional_linkages():
        pass

    def link_up_alternative_forms(cur: Cursor):
        link_up_alternative_forms_or_spellings(cur)
