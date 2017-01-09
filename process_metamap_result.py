#!usr/bin/python
"""
Generate result report from Metamap parsed terms
Xuenan Pi
23/12/2016
"""
from utterance_process import UtteranceProcess
from time_point import detect_age, detect_time_point, detect_gender
from utility import collect_needed_semantic_types


def read_file(input_file):
    file_content = open(input_file)
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
                       "[Pharmacologic Substance]"]
    age_detected_flag = False
    for idx, utterance in enumerate(matched_utterances):
        if not age_detected_flag:
            semantic_types = collect_needed_semantic_types(utterance, age_need_types)
            if semantic_types:
                matched_utterances[idx] = detect_age(utterance)
                # detect gender
                matched_utterances[idx] = detect_gender(utterance)
                age_detected_flag = True
                continue
        # detect time point only when in the text there is disease or phenotype terms
        semantic_types = collect_needed_semantic_types(utterance, time_need_types)
        if semantic_types:
            matched_utterances[idx] = detect_time_point(utterance)
    return matched_utterances

if __name__ == '__main__':
    processed_case = process("C:\\Users\\pix1\\PycharmProjects\\CaseReport\\testcases\\fullcase2result.txt")
    matched_utterance = []
    for utterance in processed_case:
        if "Utterance text" in utterance[0][0][0].keys():
            utterance_result = UtteranceProcess(utterance).main()
            matched_utterance += [utterance_result]
    result = time_point_extraction(matched_utterance)
    # clean the mapping result like population group
    # detect the negative terms in the utterance
    # order the terms in the utterance by index
    for i in result:
        for j in i:
            print "print", j

