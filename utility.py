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
        for mapping in mapping_list:
            if mapping["Semantic Types"] in need_type:
                semantic_types += [mapping["Semantic Types"]]
    return semantic_types


def clean_mapping_result(mapping):
    mapping_result = [term for term in mapping if term[1][0] != "interventional procedure"]

    if mapping_result:
        semantic_types_list = zip(*zip(*mapping_result)[1])[1]
        if set(semantic_types_list) == {"[Time Point]"}:
            mapping_result = []
    return mapping_result


def past_regex(phrase):
    past_pattern = re.compile(r"([\s-]old|history|\sago|[Pp]ast)")
    return past_pattern.search(phrase) and True or False


def label_mapping_result(mapping, text):
    index_list = zip(*mapping)[0]
    term_list = zip(*zip(*mapping)[1])[0]
    semantic_types_list = zip(*zip(*mapping)[1])[1]
    if "[Time Point]" in semantic_types_list:
        time_index = semantic_types_list.index("[Time Point]")
        for term in mapping:
            if term[1][1] != "[Time Point]":
                start = min(term[0], index_list[time_index])
                end = max(term[0], index_list[time_index])
                related = "," not in text[start:end]
                if related:
                    if past_regex(term_list[time_index]):
                        term[0] = ("Past", term_list[time_index])
                    else:
                        term[0] = ("Current", term_list[time_index])
                else:
                    term[0] = ("Current")
            else:
                mapping.remove(term)
    else:
        for term in mapping:
            term[0] = ("Current")
    return mapping

