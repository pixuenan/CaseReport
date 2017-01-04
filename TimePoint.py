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
        self.need_types = ["[Age Group]", "[Population Group]"]

    def collect_needed_semantic_types(self, utterance):
        semantic_types = []
        for phrase in utterance[1:]:
            mapping_list = phrase["mapping"]
            for mapping in mapping_list:
                if mapping["Semantic Types"] in self.need_types:
                    semantic_types += [mapping["Semantic Types"]]
        return semantic_types

    def score_semantic_types(self, semantic_types):
        score = 0
        for semantic_type in semantic_types:
            score += self.mapping_score[semantic_type]
        return score

    def detect_age(self, utterance):
        pattern = re.compile(r"([^\s]+?)(\s|-)(year|month|week|day)(s\s|-)(old)\s(male|female|man|woman|girl|boy|lady)")
        result = pattern.search(text)
        age = ''.join(result.group(1, 2, 3, 4, 5))
        return utterance

    def detect_time_point(self, utterance):
        # if score =
        return utterance

    def time_point_extraction(self, matched_utterances):
        """ Extract time point terms"""
        for idx, utterance in enumerate(matched_utterances):
            print utterance
            semantic_types = self.collect_needed_semantic_types(utterance)
            if semantic_types:
                matched_utterances[idx] = self.detect_age(utterance)
            else:
                matched_utterances[idx] = self.detect_time_point(utterance)
        return matched_utterances

if __name__ == "__main__":
    test = MetamapParser.MetamapParser()
    print "test"
    # print test.check_semantic_type("[inch, phsu]")
    # process the case report to group the sentence, phrase and mapping result together
    processed_case = test.process("C:\\Users\\pix1\\PycharmProjects\\CaseReport\\testcases\\fullcase1result.txt")
    # turn the processed case from list into dictionary, and only keep the needed field for every mapping result
    pruned_case = test.prune(processed_case)
    matched_case = test.match(pruned_case)

    time_point_test = TimePoint()
    time_point_test.time_point_extraction(matched_case)
    # for i in matched_case:
    #     for j in i:
    #         print j
