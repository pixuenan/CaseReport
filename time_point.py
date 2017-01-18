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
    r'([pP]ast|[Aa]fter)?((\s|^)([^\s]+?)(\s|-)(year|month|week|day)(s?)(?!-|old)).+?(later|ago|prior|before|earlier)?')
    time_string_list = []
    while time_pattern.search(text):
        time_result = time_pattern.search(text)
        need_list = time_result.groups("")
        time = " ".join([need_list[0].strip(), need_list[1].strip(), need_list[-1].strip()])
        time_string_list += [time.strip()]
        text = text[time_result.end():]
    return time_string_list


def detect_history_string(text):
    """ Detect history information in the phrase.
     Result: list of detected history string.
    """
    # 3-year history, past history, history of, family history
    history_pattern = re.compile(r"((\s|^)([^\s]+?)(\s|-)(year|month|week|day)s?)?((\s|^)[fF]amily)?\s(history)")
    history_string_list = []
    while history_pattern.search(text):
        history_result = history_pattern.search(text)
        need_list = history_result.groups("")
        history = " ".join([need_list[i].strip() for i in [0, -3, -1] if need_list[i]])
        history_string_list += [history.strip()]
        text = text[history_result.end():]
    return history_string_list


def detect_year_string(text):
    """Return a list of found year string with the text, am empty list will be returned if no finding"""
    year_pattern = r"\s(20|19)([0-9]{2})[\s|\,|\.]"
    return ["".join(i) for i in re.findall(year_pattern, text)]


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


def detect_time_point(utterance, age_exist=False):
    """ Detect time point word in the sentence."""
    text = utterance[0]["Utterance text"]
    time_point_dict = dict()
    time_point_dict["Time Point"] = []

    # exclude the age string the same as the "Age" of the patient
    if not age_exist:
        time_point_dict["Time Point"] += detect_age_string(text)
    time_point_dict["Time Point"] += detect_history_string(text)
    time_point_dict["Time Point"] += detect_year_string(text)
    regex_index_result = index_in_the_list(time_point_dict["Time Point"], text)

    # exclude the time point information for medicine, leave the professional part to doctor
    if not collect_needed_semantic_types(utterance, ["[Pharmacologic Substance]"]):
        for time_string in detect_time_string(text):
            if text.index(time_string) not in regex_index_result:
                time_point_dict["Time Point"] += [time_string]

    if time_point_dict["Time Point"]:
        utterance.append(time_point_dict)
    return utterance


def detect_gender(utterance):
    genders = {"woman|women|female|girl": "Female", "man|men|male|boy": "Male"}
    for phrase in utterance[1:]:
        if "Age" in phrase["mapping"][0].keys():
            idx = 0
            while idx < len(phrase["mapping"])-1:
                mapping = phrase["mapping"][1:][idx]
                if mapping["Semantic Types"] in ["[Population Group]", "[Age Group]"]:
                    keys = genders.keys()
                    # female
                    if mapping["Concept Name"].lower() in keys[0]:
                        phrase["mapping"][0]["Gender"] = genders[keys[0]]
                    # male
                    elif mapping["Concept Name"].lower() in keys[1]:
                        phrase["mapping"][0]["Gender"] = genders[keys[1]]
                    # delete the mapped term
                    phrase["mapping"].remove(mapping)
                else:
                    idx += 1
    return utterance


def past_regex(text):
    past_pattern = re.compile(r"([\s-]old|history|\sago|\sprior|\sbefore|\searlier|\sprior|[Pp]ast)")
    year_pattern = re.compile(r"(20|19)([0-9]{2})")
    return (past_pattern.search(text) or year_pattern.search(text)) and True or False

if __name__=="__main__":
    # s = "A 44-year-old white man with a past medical history of viral myocarditis, reduced left ventricular function, and continuous beta-blocker therapy, collapsed on the street."
    # s = "A 29-year-old Moroccan man presented to our hospital with a 6-month history of headache in his left skull, associated with homolateral facial pain, numbness, dip-lopia, exophthalmia, eye watering, and an episode of epi-staxis.'"
    # print detect_history_string(s)
    # s = "The patient was in her usual good health until 5 days earlier, when she started to have chills and fever. Jaundice had become manifest 2 days earlier."
    print past_regex(s)






