#!usr/bin/python
"""
Utility functions.
Xuenan Pi
06/10/2017
"""


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
        for mapping in mapping_list:
            if mapping["Semantic Types"] in need_type:
                semantic_types += [mapping["Semantic Types"]]
    return semantic_types
