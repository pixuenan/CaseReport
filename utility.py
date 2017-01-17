#!usr/bin/python
"""
Utility functions.
Xuenan Pi
06/10/2017
"""
import re

def index_in_the_list(result_list, text):
    """ Return the index of the regex result in the text."""
    index_list = []
    for result in result_list:
        index = text.index(result)
        index_list += [index]
    return index_list


def collect_needed_semantic_types(utterance, need_type):
    semantic_types = []
    for phrase in utterance[1:]:
        mapping_list = phrase["mapping"]
        if "Age" in mapping_list[0].keys():
            mapping_list = mapping_list[1:]
        for mapping in mapping_list:
            if mapping["Semantic Types"] in need_type:
                semantic_types += [mapping["Semantic Types"]]
    return semantic_types


def file_in_the_folder(folder_name):
    """Return the file name under a folder."""
    from os import listdir
    from os.path import isfile, join
    files = [f for f in listdir(folder_name) if isfile(join(folder_name, f))]
    return files

if __name__=="__main__":
    print file_in_the_folder("C:\\Users\\pix1\\PycharmProjects\\CaseReport\\testcases\\JMCR\\")





