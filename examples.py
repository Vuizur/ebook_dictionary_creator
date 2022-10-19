from ebook_dictionary_creator import DictionaryCreator

dc = DictionaryCreator("Spanish")
dc.download_data_from_kaikki()
dc.create_database()
dc.export_to_tabfile()
