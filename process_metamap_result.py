#!usr/bin/python
"""
Generate result report from Metamap parsed terms
Xuenan Pi
23/12/2016
"""
import json
from utterance_process import UtteranceProcess
from BSON_report import BSONReport
from label_terms import LabelTerms
from time_point import detect_age, detect_time_point, detect_gender
from utility import collect_needed_semantic_types, file_in_the_folder


def read_file(input_file):
    file_content = open(input_file)
    if input_file.endswith(".json"):
        data = json.loads(file_content.read())
        result_list = data["MetaMap result"]
    else:
        result_list = file_content.readlines()
    file_content.close()
    return clean_none_head(result_list)


def clean_none_head(result_list):
    """ Remove the None. at the beginning of the sentence."""
    for idx, sentence in enumerate(result_list):
        if sentence.startswith("None."):
            result_list[idx] = sentence[5:]
        else:
            result_list[idx] = sentence.strip()
    return result_list


def group(result_list, break_word):
    """Group the result in the list between the break word together."""
    element_list = []
    element = []
    for result_idx, result in enumerate(result_list):
        if result.strip().startswith(break_word) and element:
            element_list += [element]
            element = []
        elif result_idx == len(result_list) - 1:
            element += [result.strip()]
            element_list += [element]
        else:
            element += [result.strip()]
    return element_list


def convert(element):
    """Convert the element string "Id: 1" to dictionary {"Id": "1"}."""
    element_dict = {}
    for item in element:
        item_key, item_value = item.split(':', 1)
        element_dict[item_key] = item_value.strip()
    return element_dict


def process(input_file):
    """"""
    result_list = read_file(input_file)
    # group the result from one sentence together
    grouped_utterance = []
    utterances = group(result_list, "Utterance:")
    for utterance in utterances:
        # group the result from one phrase together
        grouped_phrases = []
        phrases = group(utterance, "Phrase:")
        for phrase in phrases:
            grouped_mappings = []
            mappings = group(phrase, "Map Score:")
            # remove the repetitive mapping result
            for mapping in mappings:
                terms = group(mapping, "Score:")
                # convert the string into dictionary format
                grouped_mappings += [[convert(term) for term in terms]]
            grouped_phrases += [grouped_mappings]
        grouped_utterance += [grouped_phrases]
    return grouped_utterance


def time_point_extraction(matched_utterances):
    """ Extract time point terms"""
    age_need_types = ["[Age Group]", "[Population Group]"]

    time_need_types = ["[Disease or Syndrome]", "[Neoplastic Process]", "[Sign or Symptom]",
                       "[Pathologic Function]", "[Finding]", "[Mental or Behavioral Dysfunction]",
                       "[Pharmacologic Substance]", "[Therapeutic or Preventive Procedure]"]
    age_detected_flag = False
    for idx, utterance in enumerate(matched_utterances):
        if not age_detected_flag:
            semantic_types = collect_needed_semantic_types(utterance, age_need_types)
            if semantic_types:
                # detect age
                matched_utterances[idx] = detect_age(utterance)
                # detect gender
                matched_utterances[idx] = detect_gender(utterance)
                age_detected_flag = True

        semantic_types = collect_needed_semantic_types(utterance, time_need_types)
        if semantic_types:
            matched_utterances[idx] = detect_time_point(utterance, age_exist=age_detected_flag)
    return matched_utterances


def main(input_file):
    # group utterance
    grouped_utterances = process(input_file)

    # match utterance between semantic types and sources
    matched_utterances = []
    for utterance in grouped_utterances:
        # print utterance
        if "Utterance text" in utterance[0][0][0].keys():
            utterance_result = UtteranceProcess(utterance).match()
            # print utterance_result
            matched_utterances += [utterance_result]

    # detect time point string in the utterance
    time_point_detected_utterances = time_point_extraction(matched_utterances)

    # label time point string to the mapped terms
    time_point_labeled_utterances = []
    for utterance in time_point_detected_utterances:
        time_point_labeled_utterances += [LabelTerms(utterance).main()]

    # generate report
    report = BSONReport()
    report.generate_report(time_point_labeled_utterances, input_file.split(".")[0] + ".MetaMap.processed.json")


if __name__ == '__main__':
    # folder_name = "C:\\Users\\pix1\\PycharmProjects\\CaseReport\\testcases\\JMCR\\"
    # for file_name in file_in_the_folder(folder_name):
    #     if file_name.endswith(".MetaMap.json"):
    #         print file_name
    #         main(folder_name + file_name)
    #         print "finished", file_name
    file_name = "C:\\Users\\pix1\\PycharmProjects\\CaseReport\\testcases\\JMCR\\0b2ccea4dfe3d9e11b7c43eb4182ade4JMCR.MetaMap.json"
    main(file_name)



