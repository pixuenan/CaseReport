#!usr/bin/python
"""
Extract the time point information include age from MetaMap parsed result.
Xuenan Pi
23/12/2016
"""
import re
from utility import index_in_the_list, collect_needed_semantic_types


age_pattern = re.compile(r"([^\s]+?)(\s|-)(year|month|week|day)(s\s|-)(old)")


def detect_age_string(text):
    """ Detect age information in the phrase.
     Result: list of detected age string.
    """
    age_string_list = []
    while age_pattern.search(text):
        age_result = age_pattern.search(text)
        age = ''.join(age_result.group(1, 2, 3, 4, 5))
        age_string_list += [age]
        text = text[age_result.end():]
    return age_string_list


def detect_time_string(text):
    """ Detect age information in the phrase.
     Result: list of detected age string.
    """
    # past three years, three years ago, 4 days later, after 7 weeks
    time_pattern = re.compile(
        r"([pP]ast|[Aa]fter)?((\s|^)([^\s]+?)(\s|-)(year|month|week|day)(s?)(?!-|old)).+?(later|ago)?")
    time_string_list = []
    while time_pattern.search(text):
        time_result = time_pattern.search(text)
        need_list = list(time_result.groups(""))
        time = " ".join([need_list[0], need_list[1], need_list[-1]])
        time_string_list += [time.strip()]
        text = text[time_result.end():]
    return time_string_list


def detect_history_string(text):
    """ Detect history information in the phrase.
     Result: list of detected history string.
    """
    # 3-year history, past history, history of
    history_pattern = re.compile(r"((\s|^)([^\s]+?)(\s|-)(year)s?)?\s(history)")
    history_string_list = []
    while history_pattern.search(text):
        history_result = history_pattern.search(text)
        need_list = list(history_result.groups(""))
        history = " ".join([need_list[0], need_list[-1]])
        history_string_list += [history.strip()]
        text = text[history_result.end():]
    return history_string_list


def detect_age(utterance):
    """ Detect age information in the phrase, if detected, add dictionary {"Age": age} to the phrase mapping result
    """
    text = utterance[0]["Utterance text"]
    result = age_pattern.search(text)
    if result:
        age = ''.join(result.group(1, 2, 3, 4, 5))
        age_dict = dict()
        age_dict["Age"] = age
        utterance[1]["mapping"].insert(0, age_dict)
    return utterance


def detect_time_point(utterance):
    """ Detect time point word in the sentence."""
    ori_text = utterance[0]["Utterance text"]
    time_point_dict = dict()
    time_point_dict["Time Point"] = []
    text_for_age_detec = text_for_history_detec = text_for_time_detec = ori_text

    time_point_dict["Time Point"] += detect_age_string(text_for_age_detec)
    time_point_dict["Time Point"] += detect_history_string(text_for_history_detec)
    regex_index_result = index_in_the_list(time_point_dict["Time Point"], ori_text)

    # exclude the time point information for medicine, leave the professional part to doctor
    if not collect_needed_semantic_types(utterance, ["[Pharmacologic Substance]"]):
        for time_string in detect_time_string(text_for_time_detec):
            if ori_text.index(time_string) not in regex_index_result:
                time_point_dict["Time Point"] += [time_string]

    if time_point_dict["Time Point"]:
        utterance.insert(1, time_point_dict)
    return utterance


def detect_gender(utterance):
    genders = ["Woman", "Man", "Female", "Male", "Boy", "Girl"]
    for phrase in utterance[1:]:
        if "Age" in phrase["mapping"][0].keys():
            gender_dict = dict()
            for mapping in phrase["mapping"][1:]:
                if mapping["Semantic Types"] == "[Population Group]":
                    if mapping["Concept Name"] in genders:
                        gender_dict["Gender"] = mapping["Concept Name"]
                    phrase["mapping"].remove(mapping)
            phrase["mapping"].insert(1, gender_dict)
    return utterance






