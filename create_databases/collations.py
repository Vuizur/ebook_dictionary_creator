#TODO: This should be finished

def collate_yo_ac_case_insensitive(string1: str, string2: str):
    string1 = string1.translate(translation_table_ap_yo).lower()
    string2 = string2.translate(translation_table_ap_yo).lower()

    if string1 < string2:
        return -1
    elif string1 > string2:
        return 1
    else:
        return 0