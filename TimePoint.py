#!usr/bin/python
"""
Extract the time point information include age from MetaMap parsed result.
Xuenan Pi
23/12/2016
"""
import MetamapParser
import re
from utility import index_in_the_list

class TimePoint:
    def __init__(self):
        # score the mapping result
        self.age_need_types = ["[Age Group]", "[Population Group]"]

        self.time_need_types = ["[Disease or Syndrome]", "[Neoplastic Process]", "[Sign or Symptom]",
                                "[Pathologic Function]", "[Finding]", "[Mental or Behavioral Dysfunction]",
                                "[Pharmacologic Substance]"]

        self.age_pattern = re.compile(r"([^\s]+?)(\s|-)(year|month|week|day)(s\s|-)(old)")

    def collect_needed_semantic_types(self, utterance, need_type):
        semantic_types = []
        for phrase in utterance[1:]:
            mapping_list = phrase["mapping"]
            for mapping in mapping_list:
                if mapping["Semantic Types"] in need_type:
                    semantic_types += [mapping["Semantic Types"]]
        return semantic_types

    def detect_age(self, utterance):
        """ Detect age information in the phrase, if detected, add dictionary {"Age": age} to the phrase mapping result
        """
        text = utterance[0]["Utterance text"]
        result = self.age_pattern.search(text)
        if result:
            age = ''.join(result.group(1, 2, 3, 4, 5))
            age_dict = dict()
            age_dict["Age"] = age
            utterance[1]["mapping"].insert(0, age_dict)
        return utterance

    def detect_age_string(self, text):
        """ Detect age information in the phrase.
         Result: list of detected age string.
        """
        age_string_list = []
        while self.age_pattern.search(text):
            age_result = self.age_pattern.search(text)
            age = ''.join(age_result.group(1, 2, 3, 4, 5))
            age_string_list += [age]
            text = text[age_result.end():]
        return age_string_list

    def detect_time_string(self, text):
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

    def detect_history_string(self, text):
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

    def detect_time_point(self, utterance):
        """ Detect time point word in the sentence."""
        ori_text = utterance[0]["Utterance text"]
        time_point_dict = dict()
        time_point_dict["Time Point"] = []
        text_for_age_detec = text_for_history_detec = text_for_time_detec = ori_text

        time_point_dict["Time Point"] += self.detect_age_string(text_for_age_detec)
        time_point_dict["Time Point"] += self.detect_history_string(text_for_history_detec)
        regex_index_result = index_in_the_list(time_point_dict["Time Point"], ori_text)

        for time_string in self.detect_time_string(text_for_time_detec):
            if ori_text.index(time_string) not in regex_index_result:
                time_point_dict["Time Point"] += [time_string]

        if time_point_dict["Time Point"]:
            utterance.insert(1, time_point_dict)
        return utterance

    def time_point_extraction(self, matched_utterances):
        """ Extract time point terms"""
        age_detected_flag = False
        for idx, utterance in enumerate(matched_utterances):
            if not age_detected_flag:
                semantic_types = self.collect_needed_semantic_types(utterance, self.age_need_types)
                if semantic_types:
                    matched_utterances[idx] = self.detect_age(utterance)
                    age_detected_flag = True
                    continue
            # detect time point only when in the text there is disease or phenotype terms
            semantic_types = self.collect_needed_semantic_types(utterance, self.time_need_types)
            if semantic_types:
                matched_utterances[idx] = self.detect_time_point(utterance)
        return matched_utterances

if __name__ == "__main__":
    test = MetamapParser.MetamapParser()
    print "test"
    # process the case report to group the sentence, phrase and mapping result together
    processed_case = test.process("C:\\Users\\pix1\\PycharmProjects\\CaseReport\\testcases\\fullcase2result.txt")
    # turn the processed case from list into dictionary, and only keep the needed field for every mapping result
    pruned_case = test.prune(processed_case)
    matched_case = test.match(pruned_case)

    time_point_test = TimePoint()
    result = time_point_test.time_point_extraction(matched_case)
    for i in result:
        print i[0]
        for j in i[1:]:
            if 'Time Point' in j.keys():
                print "Time Point: ", j['Time Point']
            elif 'mapping' in j.keys():
                for z in j['mapping']:
                    if 'Age' in z.keys():
                        print "Age: ", z['Age']
                    else:
                        print z['Concept Name'], z['Semantic Types']
    #     for j in i:
    #         print j