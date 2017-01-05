#!usr/bin/python
"""
Extract the time point information include age from MetaMap parsed result.
Xuenan Pi
23/12/2016
"""
import MetamapParser
import re

class TimePoint:
    def __init__(self):
        # score the mapping result
        self.age_need_types = ["[Age Group]", "[Population Group]"]

        self.time_need_types = ["[Disease or Syndrome]", "[Neoplastic Process]", "[Sign or Symptom]",
                                      "[Pathologic Function]", "[Finding]", "[Mental or Behavioral Dysfunction]"]

        self.age_pattern = re.compile(r"([^\s]+?)(\s|-)(year|month|week|day)(s\s|-)(old)")
        # past three years, three years ago, 4 days later, after 7 weeks
        self.time_pattern = re.compile(
            r"([pP]ast|[Aa]fter)?(\s|^)([^\s]+?)(\s|-)(year|month|week|day)(s?)(?!-|old).+?(later|ago)?")
        result = ''.join(list(result.groups(""))).strip()
        # 3-year history, past history, history of
        self.history_pattern = re.compile(r"")

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

    def detect_time_point(self, utterance):
        """ Detect time point word in the sentence."""
        ori_text = utterance[0]["Utterance text"]
        time_point_dict = dict()
        time_point_dict["Time Point"] = []
        text_for_age_detec, text_for_history_detec, text_for_time_detec = ("%s" % ori_text)*3

        while self.age_pattern.search(text_for_age_detec):
            age = self.age_pattern.search(text_for_age_detec)
            time_point_dict["Time Point"] += [age]
            text_for_age_detec = text_for_age_detec[age.end():]

        while self.time_pattern.search(text_for_time_detec):
            time_point = self.time_pattern.search(text_for_time_detec)
            time_point_dict["Time Point"] += [time_point]
            text_for_time_detec = text_for_time_detec[time_point.end():]

        while self.history_pattern.search(text_for_history_detec):
            history_point = self.history_pattern.search(text_for_history_detec)
            time_point_dict["Time Point"] += [history_point]
            text_for_history_detec = text_for_history_detec[history_point.end():]
        utterance.insert(0, time_point_dict)
        return utterance

    def time_point_extraction(self, matched_utterances):
        """ Extract time point terms"""
        age_detected_flag = False
        for idx, utterance in enumerate(matched_utterances):
            print utterance
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
    # print test.check_semantic_type("[inch, phsu]")
    # process the case report to group the sentence, phrase and mapping result together
    processed_case = test.process("C:\\Users\\pix1\\PycharmProjects\\CaseReport\\testcases\\fullcase2result.txt")
    # turn the processed case from list into dictionary, and only keep the needed field for every mapping result
    pruned_case = test.prune(processed_case)
    matched_case = test.match(pruned_case)

    time_point_test = TimePoint()
    time_point_test.time_point_extraction(matched_case)
    # for i in matched_case:
    #     for j in i:
    #         print j
